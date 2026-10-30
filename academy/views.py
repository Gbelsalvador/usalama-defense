from django.shortcuts import get_object_or_404, render
from .models import Scam, Situation

def scam_list(request):
    return render(request, "academy/scam_list.html", {"scams": Scam.objects.filter(actif=True)})

def scam_detail(request, slug):
    return render(request, "academy/scam_detail.html", {"scam": get_object_or_404(Scam, slug=slug, actif=True)})

def situation_list(request):
    return render(request, "academy/situation_list.html", {"situations": Situation.objects.all()})

def situation_detail(request, slug):
    return render(request, "academy/situation_detail.html", {"s": get_object_or_404(Situation, slug=slug)})
