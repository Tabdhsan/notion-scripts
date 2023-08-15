from typing import List, Dict, Union
from custom_types import MediaTypes
from tmdb_crud_and_cleanup import get_media_details_wrapper, get_media_id


def get_all_media_details_from_tmdb(
    media_from_notion_rows: List[List[str]],
) -> Dict[str, Union[Dict[str, dict], List[str]]]:
    """
    Fetches media details from The Movie Database using [media_name, media_type, notion_id] for each row from Notion.
    Returns a dictionary with a list of failed notion ids and media details for all successful media entries.
    """
    all_media_details: Dict[str, Union[Dict[str, dict], List[str]]] = {
        "success": {},
        "fail": [],
    }

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


def get_genre_obj_list(
    genres_from_new_entries: List[str], all_genres_archive: Dict[str, dict]
) -> List[dict]:
    """
    Retrieves genre objects from the provided genre list and genre archive.
    """
    updated_genres_list = []
    for genre in genres_from_new_entries:
        if genre == "sci-fi":
            genre = "science fiction"
        updated_genres_list.append(all_genres_archive[genre])
    return updated_genres_list


def get_director_producer_obj_list(
    media_type: MediaTypes,
    individuals_from_new_entries: List[str],
    individuals_archive: Dict[str, dict],
) -> List[dict]:
    """
    Retrieves director or producer objects from the provided individuals list and archive.
    """
    default_for_tv = [{"name": "TV"}]

    if media_type == "tv":
        return default_for_tv

    return [
        individuals_archive.get(individual, {"name": individual})
        for individual in individuals_from_new_entries
    ]
