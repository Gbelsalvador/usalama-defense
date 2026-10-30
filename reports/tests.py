from django.test import TestCase
from django.urls import reverse

from .forms import anonymiser
from .models import Report


class ReportTests(TestCase):
    def test_anonymiser_masks_contact_details(self):
        text = "Call +243 812 345 678 or test@example.com at https://example.org"

        result = anonymiser(text)

        self.assertIn("[numéro]", result)
        self.assertIn("[email]", result)
        self.assertIn("[lien]", result)
        self.assertNotIn("812 345 678", result)
        self.assertNotIn("test@example.com", result)
        self.assertNotIn("https://example.org", result)

    def test_report_requires_consent(self):
        response = self.client.post(
            reverse("reports:form"),
            {"texte": "Message suspect", "type_arnaque": "SMS"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), 0)

    def test_report_stores_anonymized_text_after_consent(self):
        response = self.client.post(
            reverse("reports:form"),
            {
                "texte": "Call +243 812 345 678 or test@example.com at https://example.org",
                "type_arnaque": "SMS",
                "consentement": "on",
            },
        )

        self.assertRedirects(response, reverse("reports:thanks"))
        report = Report.objects.get()
        self.assertIn("[numéro]", report.texte)
        self.assertIn("[email]", report.texte)
        self.assertIn("[lien]", report.texte)
        self.assertEqual(report.type_arnaque, "SMS")