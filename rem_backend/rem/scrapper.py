from rem_backend.settings import NEWS_API_KEY
from django.http import HttpRequest
import requests
from app_store_scraper import AppStore
from google_play_scraper import app, Sort, reviews, search
from ntscraper import Nitter
from langdetect import detect
import re


def appstore_scraper(query, country="us", limit=10):
    url = "https://itunes.apple.com/search"
    params = {"term": query, "country": country, "entity": "software", "limit": limit}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        apps = []
        reviews = []
        for app in data.get("results", []):
            apps.append(
                {
                    "app_name": app.get("trackName"),
                    "app_id": app.get("trackId"),
                }
            )

        for app in apps:
            review = AppStore(
                country=country, app_name=app["app_name"], app_id=app["app_id"]
            )
            review.review(how_many=limit)
            reviews.append(review.reviews)
            return reviews

    else:
        return {
            "error": "Failed to retrive data. Status code: " + str(response.status_code)
        }


def googleplay_scraper(query, limit=10):
    # apps = search(query, n_hits=5)
    # reviews = []
    # for app in apps:
    #     app_id = app["appId"]
    #     review = reviews(app_id, lang="en", count=limit, sort=Sort.NEWEST)
    #     reviews.append(review)
    # return reviews
    pass


def news_scraper(query, limit=10):
    url = (
        "https://newsapi.org/v2/top-headlines?category=technology&language=en&"
        f"q={query}&"
        f"apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url)
    return response.json()

scraper = Nitter()

def x_twitter_scraper(query, limit=10):
    pass
