from typing import TypedDict


class Review(TypedDict):
    name: str
    title: str
    posted_on: str
    stars: int
    review_text: str
    summary: str
    percent:str