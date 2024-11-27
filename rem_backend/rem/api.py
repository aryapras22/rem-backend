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
from rem.preprocessing import preprocess
from rem.spacy import extract_goals
from rem.userstories import createUserStories
from rem.usecase import createUseCaseDiagram


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
        return query_collection.find_one({"_id": id}).get("sources", {}).get("news", [])
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
        return query_collection.find_one({"_id": id}).get("sources", {}).get("appstore", [])
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
        return query_collection.find_one({"_id": id}).get("sources", {}).get("playstore", [])
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
        return query_collection.find_one({"_id": id}).get("sources", {}).get("xtwitter", [])
    else:
        return {"error": "Invalid scraper type"}


@api.get("preprocessing/")
def preprocessing(request, id: str):
    data = preprocess(id)
    query_collection.update_one(
        {"_id": id},
        {
            "$set": {
                "preprocessed_data": data,
            },
        },
    )
    return query_collection.find_one({"_id": id}).get("preprocessed_data", {})

@api.get("user_story/")
def user_story(request, id:str):
    extract_goals(id)
    return query_collection.find_one({"_id": id}).get("user_stories", {})

@api.get("getstories/")
def get_stories(request, id:str):
    createUserStories(id)
    return query_collection.find_one({"_id": id}).get("stories", {})

@api.get("usecase/")
def get_usecase(request, id:str):
    data = createUseCaseDiagram(id)
    query_collection.update_one({"_id": id}, {"$set": {"usecases": data}})
    return query_collection.find_one({"_id": id}).get("usecases", {})