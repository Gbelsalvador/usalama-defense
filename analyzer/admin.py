from django.contrib import admin
from .models import Rule
admin.site.register(Rule, list_display=("code", "poids", "actif"))
