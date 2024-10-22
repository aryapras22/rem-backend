from rem.models import query_collection


def get_data(_id):
    return query_collection.find_one({"_id": _id})
