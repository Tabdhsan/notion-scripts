from typing import List, Optional, TypedDict
import requests
from strenum import StrEnum
from time import sleep, strftime, gmtime

from API_KEYS import NOTION_SECRET, DB_ID, TMDB_KEY


# TODOTAB: Move types to a diff file
class PropCategories(StrEnum):
    DIRECTORS = "Directors"
    PRODUCERS = "Producers"
    GENRES = "Genres"


class MediaTypes(StrEnum):
    MOVIE = "movie"
    TV = "tv"


class SingleMediaDetailsBase(TypedDict):
    title: str
    runtime: str
    genres: List[str]
    directors: List[str]
    producers: List[str]
    trailer: str


class SingleMediaDetailsBase(TypedDict):
    title: str
    runtime: str
    genres: List[str]
    directors: List[str]
    producers: List[str]
    trailer: str


# TODOTAB: Move API logic to a different file

headers = {
    "Authorization": f"Bearer {NOTION_SECRET}",
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
}


# TODOTAB: Move helper functions


def get_db_props() -> dict:
    db_url = f"https://api.notion.com/v1/databases/{DB_ID}"
    response = requests.get(db_url, headers=headers)
    return response.json()


def get_notion_multiselect_options(category: PropCategories) -> dict:
    all_db_props = get_db_props()
    clean_dict = {}
    items = all_db_props["properties"][category]["multi_select"]["options"]
    for item in items:
        clean_dict[f'{item["name"]}'.lower()] = item
    return clean_dict


def get_db_rows_filtered_by_status(status: str) -> List[dict]:
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    db_url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    response = requests.post(db_url, headers=headers, json=payload)
    return response.json()["results"]


def get_list_of_movies_from_rows(db_rows: List[dict]) -> List[List[str]]:
    media_list = []
    # TODOTAB: Row cleanup helper function
    for row in db_rows:
        media_name = (
            row["properties"]["Name"]["title"][0]["plain_text"]
            .lower()
            .strip()
            .replace(" ", "-")
            .replace("'", "")
        )
        media_type = (
            row["properties"]["Type"]["multi_select"][0]["name"]
            .lower()
            .strip()
            .replace(" ", "-")
            .replace("'", "")
        )
        notion_id = row["id"]
        media_info = [media_name, media_type, notion_id]
        media_list.append(media_info)

    # Example: [['in-bruges', 'movie', 'd69a7d5a-492d-419e-a421-a0f2e4dc9702']]
    return media_list


def update_media_db_entry(
    notion_id: str,
    runtime: str,
    genres: List[dict],
    directors: List[dict],
    producers: List[dict],
) -> None:
    payload = {
        # TODOTAB: DB id is hardcoded
        "parent": {"database_id": "8352e1aaf48944bbb6d5f341eb4eb9f6"},
        "properties": {
            "Run Time": {
                "id": "_vCI",
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": runtime},
                        "plain_text": runtime,
                    }
                ],
            },
            "Genres": {
                "id": "GAPt",
                "type": "multi_select",
                "multi_select": genres,
            },
            "Directors": {
                "id": "XOcs",
                "type": "multi_select",
                "multi_select": directors,
            },
            "Producers": {
                "id": "XOcs",
                "type": "multi_select",
                "multi_select": producers,
            },
            "Status": {
                "id": "%7DfrT",
                "type": "status",
                "status": {
                    "id": "11ba1a35-53d7-4298-b56a-7b1de72a9441",
                    "name": "Not started",
                    "color": "red",
                },
            },
        },
    }

    # TODOTAB: Move to separate file
    url = f"https://api.notion.com/v1/pages/{notion_id}"
    requests.patch(url, headers=headers, json=payload)


def set_status_to_error(notion_id: str) -> None:
    payload = {
        "parent": {"database_id": "8352e1aaf48944bbb6d5f341eb4eb9f6"},
        "properties": {
            "Status": {
                "id": "%7DfrT",
                "type": "status",
                "status": {"id": "AuDc", "name": "ERROR", "color": "yellow"},
            },
        },
    }

    # TODOTAB: Move to separate file
    url = f"https://api.notion.com/v1/pages/{notion_id}"
    requests.patch(url, headers=headers, json=payload)


def get_streaming_links(media_name: str) -> List[str]:
    name_with_url_encoding = media_name.replace(" ", "%20")
    name_with_dashes = media_name.replace(" ", "-")
    name_with_pluses = media_name.replace(" ", "+")

    unogs_link = f"https://unogs.com/search/{name_with_url_encoding}"
    just_watch_link = f"https://www.justwatch.com/us/search?q={name_with_url_encoding}"
    look_moviess_link = f"https://lookmoviess.com/search/{name_with_dashes}"
    youtube_link = (
        f"https://www.youtube.com/results?search_query={name_with_pluses}+trailer"
    )

    return [unogs_link, just_watch_link, look_moviess_link, youtube_link]


def update_trailer_and_links(
    notion_page_id: str, media_name: str, trailer_url: str
) -> None:
    # Unogs link : https://unogs.com/search/in%20bruges
    # Just Watch link : https://www.justwatch.com/us/search?q=in%20bruges
    # Lookmoviess : https://lookmoviess.com/search/in-bruges
    # Youtube : https://www.youtube.com/results?search_query=How+I+Met+Your+Mother+trailer

    links = get_streaming_links(media_name)

    url = f"https://api.notion.com/v1/blocks/{notion_page_id}/children"
    payload = {
        "children": [
            {
                "type": "bookmark",
                "bookmark": {
                    "url": links[0],
                },
            },
            {
                "type": "bookmark",
                "bookmark": {
                    "url": links[1],
                },
            },
            {
                "type": "bookmark",
                "bookmark": {
                    "url": links[2],
                },
            },
        ]
    }

    if trailer_url:
        payload["children"].append(
            {
                "video": {
                    "type": "external",
                    "external": {"url": trailer_url},
                },
            },
        )
    else:
        payload["children"].append(
            {
                "type": "bookmark",
                "bookmark": {
                    "url": links[3],
                },
            },
        )

    requests.patch(url, headers=headers, json=payload)


def update_notion_info_wrapper(media_name, all_media_details):
    genres_from_notion = get_notion_multiselect_options(PropCategories.GENRES)
    directors_from_notion = get_notion_multiselect_options(PropCategories.DIRECTORS)
    producers_from_notion = get_notion_multiselect_options(PropCategories.PRODUCERS)

    media_details = all_media_details["success"][media_name]
    media_type = media_details["media_type"]
    updated_genres = get_genre_obj_list(media_details["genres"], genres_from_notion)

    updated_directors = get_director_producer_obj_list(
        media_type, media_details["directors"], directors_from_notion
    )

    updated_producers = get_director_producer_obj_list(
        media_type, media_details["producers"], producers_from_notion
    )

    update_media_db_entry(
        media_details["notion_id"],
        media_details["runtime"],
        updated_genres,
        updated_directors,
        updated_producers,
    )

    update_trailer_and_links(
        media_details["notion_id"], media_name, media_details["trailer"]
    )


"""
    Function below uses [media_name, media_type, notion_id] 
    for each row from Notion
    to fetch The Movie Database information

    Returns a dictionary with a list of failed
    notion ids that we could not find media info for and
    media details for all successful media entries.

"""


def get_all_media_details_from_tmdb(media_from_notion_rows: List[List[str]]):
    """
    {
        {
        "fail": ["79577177-f8bd-41ed-a269-183db814db5b"],
        "success":

            {"In Bruges": {
                "title": "In Bruges",
                "runtime": "01:48",
                "trailer": "https://www.youtube.com/watch?v=1G6W5CTaULw",
                "genres": ["comedy", "drama", "crime"],
                "director": ["Martin McDonagh"],
                "producer": ["Peter Czernin"],
                "notion_id": "d69a7d5a-492d-419e-a421-a0f2e4dc9702"
                }
        }
    }
    """

    all_media_details: dict = {"success": {}, "fail": []}

    for media_name, media_type, notion_id in media_from_notion_rows:
        media_id = get_media_id(media_type, media_name)

        if media_id:
            media_details = get_media_details_wrapper(media_id, media_type)
            media_details["notion_id"] = notion_id
            media_details["media_type"] = media_type
            title = media_details["title"]

            all_media_details["success"][title] = media_details
        else:
            all_media_details["fail"].append(notion_id)

    return all_media_details


""" 
 Functions below get notion version of 
 genre, director, producer
 tags if they already exist
"""


def get_genre_obj_list(
    genres_from_new_entries: list, all_genres_archive: dict
) -> List[dict]:
    updated_genres_list = []
    for genre in genres_from_new_entries:
        if genre == "sci-fi":
            genre = "science fiction"
        updated_genres_list.append(all_genres_archive[genre])
    return updated_genres_list


def get_director_producer_obj_list(
    media_type: MediaTypes,
    individuals_from_new_entries: list,
    individuals_archive,
) -> List[dict]:
    """Returns
    [ {"name": Nolan}, {'name': "Scorcese"}] for movies
    [ {"name":None} ] for TV

    """

    default_for_tv = [{"name": "TV"}]

    if media_type == "tv":
        return default_for_tv

    return [
        individuals_archive.get(individual, {"name": individual})
        for individual in individuals_from_new_entries
    ]


BASE_URL = "https://api.themoviedb.org/3"


def get_media_id(media_type: MediaTypes, media_title: str) -> Optional[str]:
    url = f"{BASE_URL}/search/{media_type}?api_key={TMDB_KEY}&query={media_title}"
    try:
        response = requests.get(url).json()
        if not response["results"]:
            return None
        return response["results"][0]["id"]
    except Exception as e:
        print("WE INSIDE EXCEPTION", media_type, media_title, url, e)
        return None


def get_media_details_from_id(media_type: MediaTypes, media_id: str) -> dict:
    url = f"{BASE_URL}/{media_type}/{media_id}?api_key={TMDB_KEY}&append_to_response=videos,credits"
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
        strftime("%H:%M", gmtime(details["runtime"] * 60))
        if is_movie
        else f"{seasons} Season(s) - ({episodes} Eps)"
    )

    genres = get_genres_from_details(media_type, details)

    directors, producers = get_producer_and_director(details["credits"]["crew"])

    trailer = get_trailer_url_from_details(details) if is_movie else None

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


def notion_bulk_media_list_update():
    # Get all rows from notion
    rows_from_notion = get_db_rows_filtered_by_status("*")

    # Get media list
    media_from_notion_rows = get_list_of_movies_from_rows(rows_from_notion)

    # Get details for media from notion rows

    all_media_details = get_all_media_details_from_tmdb(media_from_notion_rows)

    for media in all_media_details["success"]:
        sleep(1)
        update_notion_info_wrapper(media, all_media_details)

    for notion_id in all_media_details["fail"]:
        set_status_to_error(notion_id)


notion_bulk_media_list_update()
