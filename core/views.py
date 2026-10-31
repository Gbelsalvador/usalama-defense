from django.conf import settings
from django.http import FileResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from academy.models import Situation

def home(request):
    return render(request, "core/home.html", {"situations": Situation.objects.all()[:6]})

def service_worker(_request):
    response = FileResponse(
        open(settings.BASE_DIR / "static" / "service-worker.js", "rb"),
        content_type="application/javascript",
    )
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response

@require_POST
def set_language(request):
    language = request.POST.get("language", "")
    supported_languages = {code for code, _ in settings.LANGUAGES}
    if language not in supported_languages:
        return HttpResponseBadRequest("Langue non prise en charge.")

    next_url = request.POST.get("next", "/")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = "/"

    translation.activate(language)
    request.LANGUAGE_CODE = language
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
