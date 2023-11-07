from requests import get
from bs4 import BeautifulSoup
from constants import ODSCODES, LOW_RATING_THRESHOLD, SEARCHABLE_WORDS
from application_types import Review, Pharmacy
from openai import OpenAI
from json import loads

open_ai_client = OpenAI()


def application() -> None:
    negative_pharmacies_reviews = []
    for odscode in ODSCODES:
        print(f"Scraping {odscode}...")
        if reviews := scrape_reviews(odscode):
            pharmacies_with_reviews = Pharmacy(name=odscode, reviews=reviews)
            negative_pharmacies_reviews.append(pharmacies_with_reviews)
    print(negative_pharmacies_reviews)
    print(
        f"Found Total of {len(negative_pharmacies_reviews)} Pharmacies with negative reviews"
    )


def scrape_reviews(odscode: str) -> list[Review]:
    """Scrape reviews from the web

    Args:
        odscode (str): ODS code of the pharmacy

    Returns:
        list[Review]: List of reviews
    """
    response = get(
        f"https://www.nhs.uk/services/pharmacy/any/{odscode}/ratings-and-reviews"
    )
    if response.status_code != 200:
        print("Error fetching page")
        print(response.status_code)
        print(response.content)
        exit()
    content = response.content
    if "No ratings or reviews" in str(content):
        print("No reviews found")
        return

    soup = BeautifulSoup(content, "html.parser")
    pharmacy_reviews = soup.findAll("div", {"class": "org-review"}) or soup.findAll(
        "li", {"role": "listitem"}
    )

    negative_pharmacies_reviews = []
    for pharmacy_review in pharmacy_reviews:
        selected_review = pharmacy_review.div
        stars = [
            selected_review.find("p", {"id": f"star-rating-{number}"})
            for number in range(100)
            if selected_review.find("p", {"id": f"star-rating-{number}"}) is not None
        ]
        star_rating = int(stars[0].text[6])
        comments = selected_review.find("p", {"class": "comment-text"}).text
        posted_on = selected_review.find("span", {"class": "nhsuk-body-s"}).text
        title = (
            selected_review.find("span", {"role": "text"}).text.split("\r\n")[1].strip()
        )

        if star_rating <= LOW_RATING_THRESHOLD or any(
            word in comments for word in SEARCHABLE_WORDS
        ):
            ai_response = summarize_negative_sentiment(comments)
            review_summary = ai_response["Summary"]
            percent = ai_response[
                "Percentage Likelihood review is related to incorrect opening times"
            ]

            negative_pharmacies_reviews.append(
                Review(
                    stars=star_rating,
                    review_text=comments,
                    posted_on=posted_on,
                    title=title,
                    review_summary=review_summary,
                    percent=percent,
                )
            )
            print(negative_pharmacies_reviews)


    print(f"Found {len(negative_pharmacies_reviews)} bad reviews")
    return negative_pharmacies_reviews


def summarize_negative_sentiment(review_message: str) -> dict:
    """Summarize negative sentiment using OpenAI

    Args:
        review_message (str): Review message

    Returns:
        str: Summarized review message
    """
    with open("application/open_ai_request.txt", "r") as f:
        file = f.read()
        f.close()
    open_ai_request = file.replace("REVIEW_MESSAGE", review_message)
    chat_completion = open_ai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": open_ai_request,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion)
    return loads(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    application()
