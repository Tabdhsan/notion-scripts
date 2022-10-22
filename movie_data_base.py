import time
import requests
from typing import List, Optional
from Types import SingleMediaDetailsBase, MediaTypes


api_key = "f7963b039f335f50d513d05f89892a3e"
base_url = "https://api.themoviedb.org/3"


def get_media_id(media_type: MediaTypes, media_title: str) -> Optional[str]:
    url = f"{base_url}/search/{media_type}?api_key={api_key}&query={media_title}"
    res = requests.get(url).json()
    if not res["results"]:
        return None
    else:
        return res["results"][0]["id"]


def get_media_details_from_id(media_type: MediaTypes, media_id: str) -> dict:
    url = f"{base_url}/{media_type}/{media_id}?api_key={api_key}&append_to_response=videos,credits"
    res = requests.get(url).json()
    return res


def get_trailer_url_from_details(details: dict) -> str:
    videos = details["videos"]["results"]
    for vid in videos:
        if vid["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={vid['key']}"


def get_genres_from_details(media_type: MediaTypes, details: dict) -> List[str]:
    genres = details["genres"]
    res = []

    for item in genres:
        cur_genre = item["name"]

        if media_type == "movie":
            res.append(cur_genre.lower().strip())
        else:

            """
            Turns ['animation', 'adventure & drama', 'wester']
            into  ['animation', adventure', 'drama', western]
            """
            split_genres = map(
                lambda x: x.strip(), cur_genre.lower().strip().split("&")
            )
            res.extend(split_genres)

    return res


def get_producer_and_director(crew_list: List[dict]) -> List[list]:

    res = [[], []]
    for crew_member in crew_list:
        if crew_member["job"] == "Director":
            res[0].append(crew_member["name"])
        elif crew_member["job"] == "Producer":
            res[1].append(crew_member["name"])

    return res


def extract_info_from_details(
    media_type: MediaTypes, details: dict
) -> SingleMediaDetailsBase:
    IS_MOVIE = media_type == "movie"

    seasons = details["number_of_seasons"] if not IS_MOVIE else ""
    episodes = details["number_of_episodes"] if not IS_MOVIE else ""

    title = details["title"] if IS_MOVIE else details["name"]
    runtime = (
        time.strftime("%H:%M", time.gmtime(details["runtime"] * 60))
        if IS_MOVIE
        else f"{seasons} Season(s) - ({episodes} Eps)"
    )

    genres = get_genres_from_details(media_type, details)

    directors, producers = get_producer_and_director(details["credits"]["crew"])

    trailer = get_trailer_url_from_details(details) if IS_MOVIE else None

    return {
        "title": title,
        "runtime": runtime,
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
