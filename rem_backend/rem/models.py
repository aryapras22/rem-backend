from django.db import models
from db_connection import db

# Create your models here.
query_collection = db["query"]


# get data based on _id
def get_data(_id):
    return query_collection.find_one({"_id": _id})
