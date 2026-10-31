from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation
from django.utils.translation.trans_real import parse_accept_lang_header


class UserLanguageMiddleware(LocaleMiddleware):
    def process_request(self, request):
        supported_languages = {code for code, _ in settings.LANGUAGES}
        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if language not in supported_languages:
            language = None

        if language is None:
            for accepted_language, _ in parse_accept_lang_header(
                request.META.get("HTTP_ACCEPT_LANGUAGE", "")
            ):
                if accepted_language == "*":
                    break
                candidate = accepted_language.lower()
                if candidate in supported_languages:
                    language = candidate
                    break
                base_language = candidate.split("-", 1)[0]
                if base_language in supported_languages:
                    language = base_language
                    break

        language = language or settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = language
