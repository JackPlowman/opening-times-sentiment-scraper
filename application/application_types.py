from typing import TypedDict


class Review(TypedDict):
    stars: int
    review_text: str

class Pharmacy(TypedDict):
    name: str
    reviews: list[Review]