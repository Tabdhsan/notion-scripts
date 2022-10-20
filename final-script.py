from pprint import pprint
from movie_data_base import get_media_details_wrapper, get_media_id

from notion_code import (
    get_db_rows_filtered_by_status,
    get_list_of_movies_from_rows,
    get_notion_multiselect_options,
    update_media_db_entry,
    update_trailer,
)


# Get genre props from notion
# TODOTAB: add basic typing
# TODOTAB: use res vs response or something better to differ between resposne and result

notion_genres = get_notion_multiselect_options(
    "Genres"
)  # Returns dict with {genre: {notion genre object}}
notion_directors = get_notion_multiselect_options("Directors")
notion_producers = get_notion_multiselect_options("Producers")


# Get all rows from notion
notion_rows = get_db_rows_filtered_by_status("*")


# Get media list
all_media_list = get_list_of_movies_from_rows(notion_rows)
print(all_media_list)

# Get media info from tmdb
def get_all_media_details_from_tmdb(media_list_from_notion):
    res = {}
    for media_name, media_type, notion_id in media_list_from_notion:
        try:
            media_id = get_media_id(media_type, media_name)
        except:
            print("===============Put in an invalid entry========")
            media_id = "INVALID"
        if media_id != "INVALID":
            media_details = get_media_details_wrapper(media_id, media_name, media_type)
            res[media_details["title"]] = media_details
            res[media_details["title"]]["notion_id"] = notion_id
    return res


# List of objects with all necessary info (TODOTAB: Add typing later)
all_media_details = get_all_media_details_from_tmdb(all_media_list)

# Run notion post call with all info we have


def get_genre_obj_list(genres):
    res = []
    for genre in genres:
        res.append(notion_genres[genre])
    return res


def get_director_producer_obj_list(job, individual):
    # TODOTAB: Look into Enums
    if job == "director":
        return [notion_directors.get(individual, {"name": individual})]

    if job == "producer":
        return [notion_producers.get(individual, {"name": individual})]


def get_producer_obj_list(producer):
    return [notion_producers.get(producer, {"name": producer})]


# TODOTAB: Separate notion_genres and tmbd_genres and items by names
def update_db_entry_and_trailer(movie):
    # TODOTAB: Don't hardcode
    try:
        media_details = all_media_details[movie]
        runtime = media_details["runtime"]
        genres = media_details["genres"]
        notion_page_id = media_details["notion_id"]
        trailer_url = media_details["trailer"]
        director = media_details["director"]
        producer = media_details["producer"]

        new_genres = get_genre_obj_list(genres)
        new_directors = get_director_producer_obj_list("director", director)
        new_producers = get_director_producer_obj_list("producer", producer)
        update_media_db_entry(
            notion_page_id, runtime, new_genres, new_directors, new_producers
        )
        update_trailer(notion_page_id, trailer_url)
    except:
        print(f"{movie} skipped")


for key in all_media_details.keys():
    update_db_entry_and_trailer(key)
