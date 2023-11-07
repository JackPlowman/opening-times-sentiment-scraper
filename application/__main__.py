from requests import get
from bs4 import BeautifulSoup
from constants import ODSCODES, LOW_RATING_THRESHOLD, SEARCHABLE_WORDS
from application_types import Review, Pharmacy

def application() -> None:
    bad_pharmacies = []
    for odscode in ODSCODES:
        print(f"Scraping {odscode}...")
        if reviews := scrape_reviews(odscode):
            pharmacy_reviews = Pharmacy(name=odscode, reviews=reviews)
            print(pharmacy_reviews)
            bad_pharmacies.append(pharmacy_reviews)
    print(bad_pharmacies)


def scrape_reviews(odscode: str) -> list[Review]:
    """Scrape reviews from the web

    Args:
        odscode (str): ODS code of the pharmacy
    """
    print("Scraping reviews...")

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
    pharmacy_reviews = soup.findAll("div", {"class": "org-review"})

    for pharmacy_review in pharmacy_reviews:
        selected_review = pharmacy_review.div
        stars = [
            selected_review.find("p", {"id": f"star-rating-{number}"})
            for number in range(100)
            if selected_review.find("p", {"id": f"star-rating-{number}"}) is not None
        ]
        star_rating = int(stars[0].text[6])
        comments = selected_review.find("p", {"class": "comment-text"}).text
        bad_reviews = []
        if star_rating <= LOW_RATING_THRESHOLD or any(
            word in comments for word in SEARCHABLE_WORDS
        ):
            bad_reviews.append(Review(stars=star_rating, review_text=comments))
        return bad_reviews


if __name__ == "__main__":
    application()
