from django.test import TestCase
from django.urls import reverse

from .models import Rule


class RulesApiTests(TestCase):
    def test_api_only_returns_active_rules(self):
        Rule.objects.create(
            code="active-rule",
            patterns={"fr": ["urgent"]},
            poids=3,
            explication={"fr": "Explication"},
            conseil={"fr": "Conseil"},
            actif=True,
        )
        Rule.objects.create(
            code="inactive-rule",
            patterns={"fr": ["secret"]},
            poids=4,
            explication={"fr": "Explication"},
            conseil={"fr": "Conseil"},
            actif=False,
        )

        response = self.client.get(reverse("analyzer:rules"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([rule["code"] for rule in response.json()["regles"]], ["active-rule"])