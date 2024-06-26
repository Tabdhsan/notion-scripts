from typing import List
import requests

from custom_types import PropCategories
from notion_tmdb_wrappers import get_director_producer_obj_list, get_genre_obj_list
from API_KEYS import NOTION_DATABASE_ID, NOTION_API_KEY

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
}


def get_db_props() -> dict:
    db_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"
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
    db_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    response = requests.post(db_url, headers=headers, json=payload)
    return response.json()["results"]


def get_list_of_movies_from_rows(db_rows: List[dict]) -> List[List[str]]:
    media_list = []
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
    backdrop_path: str,
    genres: List[dict],
    directors: List[dict],
    producers: List[dict],
) -> None:
    payload = {
        "parent": {"database_id": "8352e1aaf48944bbb6d5f341eb4eb9f6"},
        "cover": {
            "type": "external",
            "external": {"url": f"https://image.tmdb.org/t/p/original{backdrop_path}"},
        },
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

    url = f"https://api.notion.com/v1/pages/{notion_id}"
    requests.patch(url, headers=headers, json=payload)


def get_streaming_links(media_name: str) -> List[str]:
    name_with_url_encoding = media_name.replace(" ", "%20")
    name_with_pluses = media_name.replace(" ", "+")

    unogs_link = f"https://unogs.com/search/{name_with_url_encoding}"
    just_watch_link = f"https://www.justwatch.com/us/search?q={name_with_url_encoding}"
    f_movies_link = f"https://fmoviesz.to/filter?keyword={name_with_pluses}"
    youtube_link = (
        f"https://www.youtube.com/results?search_query={name_with_pluses}+trailer"
    )

    return [unogs_link, just_watch_link, f_movies_link, youtube_link]


def update_trailer_and_links(
    notion_page_id: str, media_name: str, trailer_url: str
) -> None:
    # Unogs link : https://unogs.com/search/in%20bruges
    # Just Watch link : https://www.justwatch.com/us/search?q=in%20bruges
    # fmovies.to : https://fmovies.to/filter?keyword=shaun+of+the+dead
    # Youtube : https://www.youtube.com/results?search_query=How+I+Met+Your+Mother+trailer

    links = get_streaming_links(media_name)

    url = f"https://api.notion.com/v1/blocks/{notion_page_id}/children"
    children_blocks = [
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

    if trailer_url:
        children_blocks.append(
            {
                "type": "video",
                "video": {
                    "type": "external",
                    "external": {"url": trailer_url},
                },
            }
        )
    else:
        children_blocks.append(
            {
                "type": "bookmark",
                "bookmark": {
                    "url": links[3],
                },
            }
        )

    # Wrap the children blocks inside a toggle block
    payload = {
        "children": [
            {
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "My thoughts",
                            },
                        },
                    ],
                },
            },
            {
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Where to watch",
                            },
                        },
                    ],
                    "children": children_blocks,
                },
            },
        ]
    }

    res = requests.patch(url, headers=headers, json=payload)


# Update the page icon based on the media type
def update_page_icon(notion_page_id: str, media_type: str) -> None:
    url = f"https://api.notion.com/v1/pages/{notion_page_id}"

    print(media_type)
    icon = "🍿" if media_type == "movie" else "📺"

    payload = {"icon": {"type": "emoji", "emoji": icon}}

    requests.patch(url, headers=headers, json=payload)


def update_notion_info_wrapper(media_name, all_media_details):
    genres_from_notion = get_notion_multiselect_options(PropCategories.GENRES)
    directors_from_notion = get_notion_multiselect_options(PropCategories.DIRECTORS)
    producers_from_notion = get_notion_multiselect_options(PropCategories.PRODUCERS)

    media_details = all_media_details["success"][media_name]
    media_type = media_details["media_type"]
    backdrop_path = media_details["backdrop_path"]

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
        backdrop_path,
        updated_genres,
        updated_directors,
        updated_producers,
    )

    update_trailer_and_links(
        media_details["notion_id"], media_name, media_details["trailer"]
    )
    update_page_icon(media_details["notion_id"], media_type)
