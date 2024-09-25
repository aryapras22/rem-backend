from ninja import NinjaAPI
from rem.models import query_collection
from rem.scrapper import (
    news_scraper,
    appstore_scraper,
    googleplay_scraper,
    x_twitter_scraper,
)

api = NinjaAPI()


@api.get("queries/", response=list)
def get_queries(request):
    data = query_collection.find()
    serialized_data = []
    for document in data:
        document["_id"] = str(document["_id"])
        serialized_data.append(document)
    return serialized_data


@api.get("get_data/")
def get_data(request, q: str, type: str):
    if type == "news":
        return news_scraper(q)
    elif type == "appstore":
        return appstore_scraper(q)
    elif type == "googleplay":
        return googleplay_scraper(q)
    elif type == "xtwitter":
        return x_twitter_scraper(q)
    else:
        return {"error": "Invalid scraper type"}
