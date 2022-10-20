import json, requests
from pprint import pprint

# # TODOTAB: Better name


secret = "secret_krZuzei15JbUkAJnV4iFyNfX3U0NvPmmlBUJN8fH5sF"
db_id = "8352e1aaf48944bbb6d5f341eb4eb9f6"


headers = {
    "Authorization": f"Bearer {secret}",
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
}


def save_to_json(response, fileName):
    with open(f"./{fileName}.json", "w") as jsonFile:
        jsonFile.write(json.dumps(response.json()))


def get_db_rows_filtered_by_status(status):
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.post(db_url, headers=headers, json=payload)
    save_to_json(response, "db_query")

    return response.json()["results"]  # Array with row objects


def get_db_props():
    db_url = f"https://api.notion.com/v1/databases/{db_id}"
    response = requests.get(db_url, headers=headers)
    save_to_json(response, "allprops")
    return response.json()


def get_notion_multiselect_options(category):
    all_db_props = get_db_props()
    clean_dict = {}
    items = all_db_props["properties"][category]["multi_select"]["options"]
    for item in items:
        clean_dict[f'{item["name"]}'.lower()] = item
    return clean_dict


def get_list_of_movies_from_rows(db_rows):
    media_list = []  # [{mediaName: mediaType}]
    for row in db_rows:
        media_name = (
            row["properties"]["Name"]["title"][0]["plain_text"]
            .lower()
            .replace(" ", "-")
        )
        media_type = (
            row["properties"]["Type"]["multi_select"][0]["name"]
            .lower()
            .replace(" ", "-")
        )
        notion_id = row["id"]
        media_list.append([media_name, media_type, notion_id])
    return media_list


def update_media_db_entry(notion_id, runtime, genres, directors, producers):

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
    res = requests.patch(url, headers=headers, json=payload)
    print(res.text if res.status_code == 400 else "")


def update_trailer(notion_page_id, trailer_url):
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
