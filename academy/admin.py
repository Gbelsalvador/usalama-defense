from django.contrib import admin
from .models import Scam, Situation

@admin.register(Scam)
class ScamAdmin(admin.ModelAdmin):
    list_display = ("slug", "langues_validees", "actif")
    list_filter = ("actif",)

@admin.register(Situation)
class SituationAdmin(admin.ModelAdmin):
    list_display = ("slug", "langues_validees")
