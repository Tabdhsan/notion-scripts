from time import sleep
from typing import List
from MORE_HELPERS import get_all_media_details_from_tmdb
from Types import MediaTypes, PropCategories
from movie_data_base import get_media_details_wrapper, get_media_id

from notion_code import (
    get_db_rows_filtered_by_status,
    get_list_of_movies_from_rows,
    get_notion_multiselect_options,
    set_status_to_error,
    update_media_db_entry,
    update_notion_info_wrapper,
    update_trailer,
)

# TODOTAB: All files need better names
# TODOTAB: use res vs response or something better to differ between resposne and result
# TODOTAB: Move secret and db_id to separate file


def finalScriptTest():
    # Get all rows from notion
    rows_from_notion = get_db_rows_filtered_by_status("*")

    # Get media list
    media_from_notion_rows = get_list_of_movies_from_rows(rows_from_notion)

    # Get details for media from notion rows

    all_media_details = get_all_media_details_from_tmdb(media_from_notion_rows)

    for key in all_media_details["success"].keys():
        sleep(1)
        update_notion_info_wrapper(key, all_media_details)

    for id in all_media_details["fail"]:
        set_status_to_error(id)


finalScriptTest()
