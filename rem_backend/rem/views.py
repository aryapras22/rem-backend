from django.shortcuts import render
from .models import query_collection
from django.http import HttpResponse, JsonResponse, request
from rem_backend.settings import NEWS_API_KEY

# Create your views here.


def index(request):
    return HttpResponse("<h1>App is running..</h1>")


def add_query(request):
    records = {
        "query": "This is a test query",
    }
    query_collection.insert_one(records)
    return HttpResponse("<h1>Query added successfully</h1>")


def get_all_query(request):
    all_query = query_collection.find()
    return HttpResponse(all_query)


# def appstore_scraper(query, limit=10):
#     # Your existing scraper logic
#     # Returns data for the App Store
#     pass


# def googleplay_scraper(query, limit=10):
#     # Your existing scraper logic
#     # Returns data for Google Play
#     pass


# def news_scraper(query, limit=10):
#     url = (
#         "https://newsapi.org/v2/top-headlines?category=technology&language=en&"
#         f"q={query}&"
#         f"apiKey={NEWS_API_KEY}"
#     )
#     response = request.get(url)
#     return response.json()["articles"][:limit]


# def x_twitter_scraper(query, limit=10):
#     # Your existing scraper logic
#     # Returns data for X/Twitter
#     pass


# # New API view to handle requests from the frontend
# def get_data(request):
#     query = request.GET.get("q", "")
#     scraper_type = request.GET.get("type", "")

#     results = []

#     if query and scraper_type:
#         if scraper_type == "appstore":
#             results = appstore_scraper(query)
#         elif scraper_type == "googleplay":
#             results = googleplay_scraper(query)
#         elif scraper_type == "news":
#             results = news_scraper(query)
#         elif scraper_type == "twitter":
#             results = x_twitter_scraper(query)

#     return JsonResponse({"results": results})
