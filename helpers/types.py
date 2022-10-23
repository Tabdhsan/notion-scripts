from typing import List, TypedDict
from strenum import StrEnum


class PropCategories(StrEnum):
    DIRECTORS = "Directors"
    PRODUCERS = "Producers"
    GENRES = "Genres"


class MediaTypes(StrEnum):
    MOVIE = "movie"
    TV = "tv"


class SingleMediaDetailsBase(TypedDict):
    title: str
    runtime: str
    genres: List[str]
    directors: List[str]
    producers: List[str]
    trailer: str
