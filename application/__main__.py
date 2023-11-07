from requests import get
from bs4 import BeautifulSoup
from constants import ODSCODES, LOW_RATING_THRESHOLD, SEARCHABLE_WORDS
from application_types import Review, Pharmacy

def application() -> None:
    negative_pharmacies_reviews = []
    for odscode in ODSCODES:
        print(f"Scraping {odscode}...")
        if reviews := scrape_reviews(odscode):
            pharmacies_with_reviews = Pharmacy(name=odscode, reviews=reviews)
            # print(pharmacies_with_reviews)
            negative_pharmacies_reviews.append(pharmacies_with_reviews)
    # print(negative_pharmacies_reviews)
    print(f"Found Total of {len(negative_pharmacies_reviews)} Pharmacies with negative reviews")


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
    pharmacy_reviews = soup.findAll("div", {"class": "org-review"}) or soup.findAll("li", {"role": "listitem"})
    
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
        
        # print(f"Analyzing star rating...: {star_rating <= LOW_RATING_THRESHOLD}")
        # print(f"Analyzing any bad reviews...: {any(word in comments for word in SEARCHABLE_WORDS)}")

        if star_rating <= LOW_RATING_THRESHOLD or any(
            word in comments for word in SEARCHABLE_WORDS
        ):
            negative_pharmacies_reviews.append(Review(stars=star_rating, review_text=comments))
    print(f"Found {len(negative_pharmacies_reviews)} bad reviews")
    return negative_pharmacies_reviews


if __name__ == "__main__":
    application()
