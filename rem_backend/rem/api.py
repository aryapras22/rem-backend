from ninja import NinjaAPI
from rem.models import query_collection
from rem.scrapper import (
    news_scraper,
    appstore_scraper,
    googleplay_scraper,
    x_twitter_scraper,
)
import datetime
import uuid

api = NinjaAPI()


@api.get("queries/", response=list)
def get_queries(request):
    data = query_collection.find()
    serialized_data = []
    for document in data:
        document["_id"] = str(document["_id"])
        serialized_data.append(document)
    return serialized_data


@api.post("add_query/")
def add_query(request, q: str):
    _id = str(uuid.uuid4())
    query_collection.insert_one(
        {
            "_id": _id,
            "query": q,
            "timestamp": datetime.datetime.now(),
        }
    )
    return _id


@api.get("get_data/")
def get_data(request, q: str, type: str, id: str):
    if type == "news":
        newsData = news_scraper(q)
        query_collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "sources.news": newsData,
                },
            },
        )
        return newsData
    elif type == "appstore":
        appstoreData = appstore_scraper(q)
        query_collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "sources.appstore": appstoreData,
                },
            },
        )
        return appstoreData
    elif type == "playstore":
        playstoreData = googleplay_scraper(q)
        query_collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "sources.playstore": playstoreData,
                },
            },
        )
        return playstoreData
    elif type == "xtwitter":
        xtwitterData = x_twitter_scraper(q)
        query_collection.update_one(
            {"_id": id},
            {
                "$set": {
                    "sources.xtwitter": xtwitterData,
                },
            },
        )
        return xtwitterData
    else:
        return {"error": "Invalid scraper type"}


@api.get("preprocessing/")
def preprocessing(request, id: str):
    return {"error": "Not implemented yet"}
