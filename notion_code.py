from MORE_HELPERS import get_director_producer_obj_list
from MORE_HELPERS import get_genre_obj_list
import requests
from typing import List
from enum import Enum

from Types import PropCategories


# TODOTAB: Move to separate file
secret = "secret_krZuzei15JbUkAJnV4iFyNfX3U0NvPmmlBUJN8fH5sF"
db_id = "8352e1aaf48944bbb6d5f341eb4eb9f6"


headers = {
    "Authorization": f"Bearer {secret}",
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
}


def get_db_rows_filtered_by_status(status: str) -> List[dict]:
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.post(db_url, headers=headers, json=payload)
    return response.json()["results"]


def get_db_props() -> dict:
    db_url = f"https://api.notion.com/v1/databases/{db_id}"
    response = requests.get(db_url, headers=headers)
    return response.json()


def get_notion_multiselect_options(category: PropCategories) -> dict:
    all_db_props = get_db_props()
    clean_dict = {}
    items = all_db_props["properties"][category]["multi_select"]["options"]
    for item in items:
        clean_dict[f'{item["name"]}'.lower()] = item
    return clean_dict


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
    genres: List[dict],
    directors: List[dict],
    producers: List[dict],
) -> None:
    payload = {
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


def update_trailer(notion_page_id: str, trailer_url: str) -> None:
    url = f"https://api.notion.com/v1/blocks/{notion_page_id}/children"
    payload = {
        "children": [
            {
                "video": {
                    "type": "external",
                    "external": {"url": trailer_url},
                }
            }
        ]
    }
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

    if media_type == "movie":
        update_trailer(media_details["notion_id"], media_details["trailer"])
