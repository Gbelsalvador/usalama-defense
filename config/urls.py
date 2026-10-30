from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("core.urls")),
    path("bibliotheque/", include("academy.urls")),
    path("analyse/", include("analyzer.urls")),
    path("signaler/", include("reports.urls")),
]
