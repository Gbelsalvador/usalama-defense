from django.db import models
from core.i18n import tr

class Rule(models.Model):
    """Indicateur d'arnaque. patterns = {"fr": ["regex", ...], "ln": [...]}"""
    code = models.CharField(max_length=50, unique=True)
    patterns = models.JSONField()
    poids = models.PositiveSmallIntegerField(default=2)
    explication = models.JSONField()
    conseil = models.JSONField()
    actif = models.BooleanField(default=True)

    def __str__(self): return self.code

    def as_dict(self, lang):
        motifs = []
        for l in {"fr", lang}:
            motifs += self.patterns.get(l, [])
        return {"code": self.code, "patterns": motifs, "poids": self.poids,
                "explication": tr(self.explication, lang), "conseil": tr(self.conseil, lang)}
