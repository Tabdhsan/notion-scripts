from typing import List
from helpers.tmdb_crud_and_cleanup import get_media_details_wrapper, get_media_id
from helpers.types import MediaTypes


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
                backdrop_path: "/link",
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
