# genres_from_notion = get_notion_multiselect_options(
#     PropCategories.GENRES
# )  # Returns dict with {genre: {notion genre object}}
# directors_from_notion = get_notion_multiselect_options(PropCategories.DIRECTORS)
# producers_from_notion = get_notion_multiselect_options(PropCategories.PRODUCERS)


# # Get all rows from notion
# rows_from_notion = get_db_rows_filtered_by_status("*")


# # Get media list
# media_from_notion_rows = get_list_of_movies_from_rows(rows_from_notion)


# # Get media info from tmdb
# def get_all_media_details_from_tmdb(media_from_notion_rows):
#     res = {"success": {}, "fail": []}
#     """
#     {
#         "fail": ["79577177-f8bd-41ed-a269-183db814db5b"],
#         "success":

#             {"In Bruges": {
#                 "title": "In Bruges",
#                 "runtime": "01:48",
#                 "trailer": "https://www.youtube.com/watch?v=1G6W5CTaULw",
#                 "genres": ["comedy", "drama", "crime"],
#                 "director": ["Martin McDonagh"],
#                 "producer": ["Peter Czernin"],
#                 "notion_id": "d69a7d5a-492d-419e-a421-a0f2e4dc9702"
#                 }
#             }
# 	}

#     """

#     for media_name, media_type, notion_id in media_from_notion_rows:
#         media_id = get_media_id(media_type, media_name)

#         if media_id:
#             media_details = get_media_details_wrapper(media_id, media_type)
#             media_details["notion_id"] = notion_id
#             media_details["media_type"] = media_type
#             title = media_details["title"]

#             res["success"][title] = media_details
#         else:
#             res["fail"].append(notion_id)

#     return res


# List of objects with all necessary info (TODOTAB: Add typing later)

# Run notion post call with all info we have


# def get_genre_obj_list(genres):
#     res = []
#     for genre in genres:
#         if genre == "sci-fi":
#             genre = "science fiction"
#         res.append(genres_from_notion[genre])
#     return res


# def get_director_producer_obj_list(
#     media_type: MediaTypes, job: str, individuals: list
# ) -> List[dict]:
#     """Returns
#     [ {"name": Nolan}, {'name': "Scorcese"}] for movies
#     [ {"name":None} ] for TV

#     """

#     default_for_tv = [{"name": "TV"}]

#     if media_type == "tv":
#         return default_for_tv

#     if job == "director":
#         return [
#             directors_from_notion.get(director, {"name": director})
#             for director in individuals
#         ]

#     if job == "producer":
#         return [
#             producers_from_notion.get(producer, {"name": producer})
#             for producer in individuals
#         ]

# if job == "director" and not individual:
#     return [
#         directors_from_notion.get(
#             individual, {"name": individual if individual else "TV"}
#         )
#     ]

# if job == "producer":
#     return [
#         producers_from_notion.get(
#             individual, {"name": individual if individual else "TV"}
#         )
#     ]


# def create_db_entry_obj(media_details):
#     director = media_details["director"]
#     director_obj_list = get_director_producer_obj_list("director", director)
#     producer: media_details["producer"]
#     producer_obj_list = get_director_producer_obj_list("producer", producer)

#     return {
#         "notion_page_id": media_details["notion_id"],
#         "runtime": media_details["runtime"],
#         "genres": media_details["genres"],
#         "trailer_url": media_details["trailer"] if media_details["trailer"] else "",
#         "updated_directors": director_obj_list if director_obj_list else [{}],
#         "updated_producers": producer_obj_list if producer_obj_list else [{}],
#     }


# def update_db_entry_and_trailer(media):
#     media_details = all_media_details["success"][media]
#     media_type = media_details["media_type"]
#     updated_genres = get_genre_obj_list(media_details["genres"])

#     updated_directors = get_director_producer_obj_list(
#         media_type, "director", media_details["directors"]
#     )

#     updated_producers = get_director_producer_obj_list(
#         media_type, "producer", media_details["producers"]
#     )

#     update_media_db_entry(
#         media_details["notion_id"],
#         media_details["runtime"],
#         updated_genres,
#         updated_directors,
#         updated_producers,
#     )

#     if media_type == "movie":
#         update_trailer(media_details["notion_id"], media_details["trailer"])
