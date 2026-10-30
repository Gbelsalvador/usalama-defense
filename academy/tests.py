from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Scam, Situation
from analyzer.models import Rule


class LocalizedContentTests(TestCase):
    def setUp(self):
        Scam.objects.create(
            slug="test-scam",
            nom={"fr": "Titre français", "ln": "Lingala title"},
            explication={"fr": "Explication française", "ln": "Lingala explanation"},
            exemple={"fr": "Exemple français", "ln": "Lingala example"},
            signes={"fr": ["Signe français"], "ln": ["Lingala sign"]},
            erreurs={"fr": ["Erreur française"], "ln": ["Lingala mistake"]},
            protections={"fr": ["Protection française"], "ln": ["Lingala advice"]},
            langues_validees=["fr", "ln"],
        )
        Situation.objects.create(
            slug="test-situation",
            titre={"fr": "Titre français", "ln": "Lingala title"},
            actions={"fr": ["Action française"], "ln": ["Lingala action"]},
            langues_validees=["fr", "ln"],
        )

    def test_scam_detail_uses_validated_language_for_lists(self):
        response = self.client.get(
            reverse("academy:detail", args=["test-scam"]),
            HTTP_ACCEPT_LANGUAGE="ln",
        )

        self.assertContains(response, "Lingala sign")
        self.assertContains(response, "Lingala mistake")
        self.assertContains(response, "Lingala advice")
        self.assertNotContains(response, "Signe français")

    def test_situation_detail_uses_validated_language_for_actions(self):
        response = self.client.get(
            reverse("academy:situation", args=["test-situation"]),
            HTTP_ACCEPT_LANGUAGE="ln",
        )

        self.assertContains(response, "Lingala action")
        self.assertNotContains(response, "Action française")


class SeedCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed", verbosity=0)
        initial_counts = (Rule.objects.count(), Scam.objects.count(), Situation.objects.count())

        call_command("seed", verbosity=0)

        self.assertEqual(
            (Rule.objects.count(), Scam.objects.count(), Situation.objects.count()),
            initial_counts,
        )