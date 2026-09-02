from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("book/", views.book_table, name="book_table"),
    path("review/", views.add_review, name="add_review"),
    path("api/tables/", views.get_tables_api, name="get_tables_api"),
]
