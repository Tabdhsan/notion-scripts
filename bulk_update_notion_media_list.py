from time import sleep
from helpers.notion_crud_and_cleanup import (
    get_db_rows_filtered_by_status,
    get_list_of_movies_from_rows,
    set_status_to_error,
    update_notion_info_wrapper,
)
from helpers.notion_tmdb_wrappers import get_all_media_details_from_tmdb


def notion_bulk_media_list_update():
    # Get all rows from notion
    rows_from_notion = get_db_rows_filtered_by_status("*")

    # Get media list
    media_from_notion_rows = get_list_of_movies_from_rows(rows_from_notion)

    # Get details for media from notion rows

    all_media_details = get_all_media_details_from_tmdb(media_from_notion_rows)

    rows = 1
    for media in all_media_details["success"]:
        sleep(1)
        update_notion_info_wrapper(media, all_media_details)
        print(f"Updated {rows} row(s)")
        rows += 1

    rows = 1
    for notion_id in all_media_details["fail"]:
        set_status_to_error(notion_id)
        print(f"Updated {rows} Error(s)")
        rows += 1


notion_bulk_media_list_update()
