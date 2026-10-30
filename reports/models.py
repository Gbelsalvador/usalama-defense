from django.db import models

class Report(models.Model):
    texte = models.TextField()
    type_arnaque = models.CharField(max_length=60, blank=True)
    langue = models.CharField(max_length=5)
    cree_le = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-cree_le"]
    def __str__(self): return f"{self.cree_le:%d/%m/%Y} {self.type_arnaque}"
