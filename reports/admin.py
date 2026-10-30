from django.contrib import admin
from .models import Report
admin.site.register(Report, list_display=("cree_le", "type_arnaque", "langue"))
