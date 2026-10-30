from django.urls import path
from . import views
app_name = "analyzer"
urlpatterns = [
    path("", views.analyze_page, name="page"),
    path("regles.json", views.rules_json, name="rules"),
]
