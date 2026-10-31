from django import forms
from django.utils.translation import gettext_lazy as _


class AssistantForm(forms.Form):
    question = forms.CharField(
        label=_("Décris la situation"),
        max_length=4000,
        widget=forms.Textarea(attrs={"rows": 6, "autocomplete": "off"}),
    )
    consentement = forms.BooleanField(
        label=_("J'accepte l'envoi de ma description à Groq pour obtenir une réponse."),
        error_messages={"required": _("Votre accord est nécessaire pour utiliser l'assistant.")},
    )
