from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import get_language
from .models import Rule

def analyze_page(request):
    return render(request, "analyzer/analyze.html")

def rules_json(request):
    """Règles envoyées au navigateur : l'analyse du message se fait sur l'appareil,
    le texte de l'utilisateur n'est jamais envoyé au serveur."""
    lang = get_language() or "fr"
    return JsonResponse({
        "lang": lang,
        "seuils": {"a_verifier": 3, "eleve": 6},
        "regles": [r.as_dict(lang) for r in Rule.objects.filter(actif=True)],
    })
