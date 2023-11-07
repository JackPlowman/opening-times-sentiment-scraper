from requests import get
from bs4 import BeautifulSoup
from constants import ODSCODES, LOW_RATING_THRESHOLD, SEARCHABLE_WORDS

def application() -> None:
    for odscode in ODSCODES:
        print(f"Scraping {odscode}...")
        scrape_reviews(odscode)


def scrape_reviews(odscode: str) -> None:
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
    reviews = soup.findAll("div", {"class": "org-review"})

    for review in reviews:
        new_review = review.div
        stars = [
            new_review.find("p", {"id": f"star-rating-{number}"})
            for number in range(100)
            if new_review.find("p", {"id": f"star-rating-{number}"}) is not None
        ]
        star_rating = int(stars[0].text[6])
        comments = new_review.find("p", {"class": "comment-text"}).text
        bad_reviews = []
        # print(f"Analyzing star rating...: {star_rating <= LOW_RATING_THRESHOLD}")
        # print(f"Analyzing any bad reviews...: {any(word in comments for word in SEARCHABLE_WORDS)}")
        if star_rating <= LOW_RATING_THRESHOLD or any(
            word in comments for word in SEARCHABLE_WORDS
        ):
            bad_reviews.append({"stars":star_rating, "review_text":comments})
        print(bad_reviews)


if __name__ == "__main__":
    application()
