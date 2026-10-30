from django.db import models
from core.i18n import tr

class Scam(models.Model):
    """Fiche d'arnaque. Les champs texte sont des dictionnaires {"fr": "...", "ln": "..."}."""
    slug = models.SlugField(unique=True)
    nom = models.JSONField()
    explication = models.JSONField()
    exemple = models.JSONField()
    signes = models.JSONField(help_text='Liste par langue : {"fr": ["...", "..."]}')
    erreurs = models.JSONField(help_text="Erreurs à éviter, liste par langue")
    protections = models.JSONField(help_text="Mesures de protection, liste par langue")
    audio = models.JSONField(default=dict, blank=True, help_text='{"ln": "/static/audio/x.mp3"}')
    langues_validees = models.JSONField(default=list, help_text='Ex: ["fr", "ln"]')
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self): return self.slug
    def t(self, field): return tr(getattr(self, field), validated=self.langues_validees)

class Situation(models.Model):
    """Rubrique « Que dois-je faire ? »"""
    slug = models.SlugField(unique=True)
    titre = models.JSONField()
    actions = models.JSONField(help_text="Actions prioritaires, liste par langue")
    langues_validees = models.JSONField(default=list)

    class Meta:
        ordering = ["id"]

    def __str__(self): return self.slug
    def t(self, field): return tr(getattr(self, field), validated=self.langues_validees)
