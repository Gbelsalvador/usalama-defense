import json
from io import BytesIO
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .llm import GroqError, ask_groq, redact_sensitive_data
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


class AssistantTests(TestCase):
    def test_assistant_requires_explicit_consent(self):
        with patch("analyzer.views.ask_groq") as ask:
            response = self.client.post(
                reverse("analyzer:assistant"),
                {"question": "Un message me demande un code."},
            )

        self.assertEqual(response.status_code, 200)
        ask.assert_not_called()

    @override_settings(GROQ_API_KEY="")
    def test_assistant_shows_configuration_error(self):
        response = self.client.post(
            reverse("analyzer:assistant"),
            {"question": "Un message me demande un code.", "consentement": "on"},
        )

        self.assertContains(response, "GROQ_API_KEY")

    @override_settings(GROQ_API_KEY="test-key", GROQ_MODEL="openai/gpt-oss-20b")
    @patch("analyzer.llm.urlopen")
    def test_groq_request_uses_configured_model_and_redacts_secrets(self, urlopen):
        urlopen.return_value = BytesIO(
            b'{"choices":[{"message":{"content":"Ne partage pas ce code."}}]}'
        )

        answer = ask_groq(
            "Mon code PIN est 123456, écris-moi à test@example.com",
            "fr",
        )

        self.assertEqual(answer, "Ne partage pas ce code.")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "openai/gpt-oss-20b")
        self.assertIn("français", payload["messages"][0]["content"])
        self.assertNotIn("123456", payload["messages"][1]["content"])
        self.assertNotIn("test@example.com", payload["messages"][1]["content"])
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

    @override_settings(GROQ_API_KEY="")
    def test_groq_requires_api_key(self):
        with self.assertRaisesMessage(GroqError, "GROQ_API_KEY"):
            ask_groq("Situation à vérifier", "fr")

    def test_redact_sensitive_data_removes_links_and_phone_numbers(self):
        result = redact_sensitive_data(
            "Clique https://example.org ou appelle +243 812 345 678."
        )

        self.assertNotIn("https://example.org", result)
        self.assertNotIn("+243 812 345 678", result)