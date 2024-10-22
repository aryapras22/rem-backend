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
