import re
from django import forms
from django.utils.translation import gettext_lazy as _

class ReportForm(forms.Form):
    texte = forms.CharField(label=_("Message ou description"), widget=forms.Textarea(attrs={"rows": 6}), max_length=2000)
    type_arnaque = forms.CharField(label=_("Type d'arnaque (facultatif)"), required=False, max_length=60)
    consentement = forms.BooleanField(label=_("J'accepte d'envoyer ce signalement anonymisé"), error_messages={"required": _("Votre accord est nécessaire pour envoyer.")})

def anonymiser(texte):
    texte = re.sub(r"https?://\S+|www\.\S+", "[lien]", texte)
    texte = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", texte)
    texte = re.sub(r"\+?\d[\d\s.-]{5,}\d", "[numéro]", texte)
    return texte
