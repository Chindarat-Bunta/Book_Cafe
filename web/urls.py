from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("book/", views.book_table, name="book_table"),
    path("review/", views.add_review, name="add_review"),
    path("api/tables/", views.get_tables_api, name="get_tables_api"),
    
    # Admin & Staff Backend
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/login/", views.admin_login, name="admin_login"),
    path("dashboard/logout/", views.admin_logout, name="admin_logout"),
    path("dashboard/toggle-table/", views.admin_toggle_table, name="admin_toggle_table"),
    path("dashboard/update-reservation/", views.admin_update_reservation, name="admin_update_reservation"),
    path("dashboard/delete-review/", views.admin_delete_review, name="admin_delete_review"),
]
