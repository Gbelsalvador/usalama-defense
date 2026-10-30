from django.urls import path
from . import views
app_name = "academy"
urlpatterns = [
    path("", views.scam_list, name="list"),
    path("arnaque/<slug:slug>/", views.scam_detail, name="detail"),
    path("urgence/", views.situation_list, name="situations"),
    path("urgence/<slug:slug>/", views.situation_detail, name="situation"),
]
