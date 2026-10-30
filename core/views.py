from django.shortcuts import render
from academy.models import Situation

def home(request):
    return render(request, "core/home.html", {"situations": Situation.objects.all()[:6]})
