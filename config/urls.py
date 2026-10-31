from django.contrib import admin
from django.urls import include, path
from core.views import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("core.urls")),
    path("bibliotheque/", include("academy.urls")),
    path("analyse/", include("analyzer.urls")),
    path("signaler/", include("reports.urls")),
]
