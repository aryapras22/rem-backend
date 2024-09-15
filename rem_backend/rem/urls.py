from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_query, name="add_query"),
    path("show/", views.get_all_query, name="get_all_query"),
]
