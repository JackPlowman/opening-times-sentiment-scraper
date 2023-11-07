from typing import TypedDict


class Review(TypedDict):
    stars: int
    title: str
    review_text: str
    posted_on: str
    review_summary: str


class Pharmacy(TypedDict):
    name: str
    reviews: list[Review]