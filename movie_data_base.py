from pprint import pprint
import time
import requests

from notion_code import save_to_json

api_key = "f7963b039f335f50d513d05f89892a3e"
base_url = "https://api.themoviedb.org/3"


def get_media_id(media_type, media_title):
    url = f"{base_url}/search/{media_type}?api_key={api_key}&query={media_title}"
    res = requests.get(url).json()
    return res["results"][0]["id"]


def get_media_details_from_id(media_type, media_id):
    url = f"{base_url}/{media_type}/{media_id}?api_key={api_key}&append_to_response=videos,credits"
    res = requests.get(url).json()
    return res


def get_trailer_url_from_details(details):
    videos = details["videos"]["results"]
    for vid in videos:
        if vid["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={vid['key']}"


def get_genres_from_details(details):
    genres = details["genres"]
    res = []
    for item in genres:
        res.append(item["name"].lower())
    return res


def get_producer_and_director(crew_list):
    res = [None, None]
    for crew_member in crew_list:
        if crew_member["job"] == "Director":
            res[0] = crew_member["name"]
        elif crew_member["job"] == "Producer":
            res[1] = crew_member["name"]
    return res


# NOTE: This only works for movies
def extract_info_from_details(details):
    new_obj = {}
    new_obj["title"] = details["title"]
    new_obj["runtime"] = time.strftime("%H:%M", time.gmtime(details["runtime"] * 60))
    new_obj["trailer"] = get_trailer_url_from_details(details)
    new_obj["genres"] = get_genres_from_details(details)
    new_obj["director"], new_obj["producer"] = get_producer_and_director(
        details["credits"]["crew"]
    )
    return new_obj


def get_media_details_wrapper(media_title, media_type):
    media_id = get_media_id(media_type, media_title)
    raw_details = get_media_details_from_id(media_type, media_id)
    clean_details = extract_info_from_details(raw_details)
    return clean_details
