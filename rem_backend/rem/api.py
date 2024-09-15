from ninja import NinjaAPI
from rem.models import query_collection

api = NinjaAPI()


@api.get("queries/", response=list)
def get_queries(request):
    data = query_collection.find()
    serialized_data = []
    for document in data:
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        serialized_data.append(document)
    return serialized_data
