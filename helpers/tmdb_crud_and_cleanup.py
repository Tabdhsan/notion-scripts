from typing import List, Optional
import time
import requests
from helpers.types import SingleMediaDetailsBase, MediaTypes
from creds import tmdb_key


BASE_URL = "https://api.themoviedb.org/3"


def get_media_id(media_type: MediaTypes, media_title: str) -> Optional[str]:
    url = f"{BASE_URL}/search/{media_type}?api_key={tmdb_key}&query={media_title}"
    response = requests.get(url).json()
    if not response["results"]:
        return None
    return response["results"][0]["id"]


def get_media_details_from_id(media_type: MediaTypes, media_id: str) -> dict:
    url = f"{BASE_URL}/{media_type}/{media_id}?api_key={tmdb_key}&append_to_response=videos,credits"
    response = requests.get(url).json()
    return response


def get_trailer_url_from_details(details: dict) -> Optional[str]:
    videos = details["videos"]["results"]
    for vid in videos:
        if vid["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={vid['key']}"


def get_genres_from_details(media_type: MediaTypes, details: dict) -> List[str]:
    genres = details["genres"]
    tmdb_genre_info = []

    for item in genres:
        cur_genre = item["name"]

        if media_type == "movie":
            tmdb_genre_info.append(cur_genre.lower().strip())
        else:
            # Turns ['animation', 'adventure & drama', 'wester'] into
            # ['animation', adventure', 'drama', western]
            split_genres = map(
                lambda x: x.strip(), cur_genre.lower().strip().split("&")
            )
            tmdb_genre_info.extend(split_genres)

    return tmdb_genre_info


def get_producer_and_director(crew_list: List[dict]) -> List[list]:
    tmdb_crew_info: List[list] = [[], []]
    for crew_member in crew_list:
        if crew_member["job"] == "Director":
            tmdb_crew_info[0].append(crew_member["name"])
        elif crew_member["job"] == "Producer":
            tmdb_crew_info[1].append(crew_member["name"])

    return tmdb_crew_info


def extract_info_from_details(
    media_type: MediaTypes, details: dict
) -> SingleMediaDetailsBase:
    is_movie = media_type == "movie"

    seasons = details["number_of_seasons"] if not is_movie else ""
    episodes = details["number_of_episodes"] if not is_movie else ""

    title = details["title"] if is_movie else details["name"]
    runtime = (
        time.strftime("%H:%M", time.gmtime(details["runtime"] * 60))
        if is_movie
        else f"{seasons} Season(s) - ({episodes} Eps)"
    )

    backdrop_path = details["backdrop_path"]

    genres = get_genres_from_details(media_type, details)

    directors, producers = get_producer_and_director(details["credits"]["crew"])

    trailer = get_trailer_url_from_details(details) if is_movie else None

    return {
        "title": title,
        "runtime": runtime,
        "backdrop_path": backdrop_path,
        "genres": genres,
        "directors": directors,
        "producers": producers,
        "trailer": trailer,
    }


def get_media_details_wrapper(
    media_id: str, media_type: MediaTypes
) -> SingleMediaDetailsBase:
    raw_details = get_media_details_from_id(media_type, media_id)
    clean_details = extract_info_from_details(media_type, raw_details)
    return clean_details
