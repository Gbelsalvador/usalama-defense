from django.test import TestCase
from django.urls import reverse


class ServiceWorkerTests(TestCase):
    def test_service_worker_allows_application_scope(self):
        response = self.client.get(reverse("core:service-worker"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertContains(response, "CACHE_URLS")


class LanguageSelectionTests(TestCase):
    def test_selected_national_language_is_remembered(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "ln", "next": "/"},
        )

        self.assertRedirects(response, "/")
        self.assertEqual(response.cookies["django_language"].value, "ln")
        page = self.client.get("/", HTTP_ACCEPT_LANGUAGE="fr")
        self.assertIn('<html lang="ln">', page.content.decode())

    def test_language_redirect_rejects_external_hosts(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "ln", "next": "https://example.com/"},
        )

        self.assertRedirects(response, "/")

    def test_language_switch_rejects_unknown_language(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "xx", "next": "/"},
        )

        self.assertEqual(response.status_code, 400)
