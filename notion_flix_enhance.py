from time import sleep
from notion_crud_and_cleanup import (
    get_db_rows_filtered_by_status,
    get_list_of_movies_from_rows,
    set_status_to_error,
    update_notion_info_wrapper,
)
from notion_tmdb_wrappers import get_all_media_details_from_tmdb


def notion_flix_enhance():
    print("Great choice of media! Let's get started...\n")
    print("Getting all rows from Notion...\n")

    # Get all rows from Notion
    rows_from_notion = get_db_rows_filtered_by_status("*")

    # Get media list
    media_from_notion_rows = get_list_of_movies_from_rows(rows_from_notion)

    # Get details for media from Notion rows
    all_media_details = get_all_media_details_from_tmdb(media_from_notion_rows)

    # Update successful rows
    rows = 1
    for media in all_media_details["success"]:
        sleep(1)  # For rate limiting reasons
        update_notion_info_wrapper(media, all_media_details)
        print(f"Updated {rows} row{'s' if rows > 1 else ''}")
        rows += 1

    # Update failed rows
    rows = 1
    for notion_id in all_media_details["fail"]:
        set_status_to_error(notion_id)
        print(f"Updated {rows} Error{'s' if rows > 1 else ''}")
        rows += 1

    print("All done, Happy Watching!🍿")


if __name__ == "__main__":
    notion_flix_enhance()
