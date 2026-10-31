import json
import logging
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
LANGUAGE_NAMES = {
    "fr": "français",
    "ln": "lingala",
    "sw": "swahili",
    "kg": "kikongo ya Leta",
    "lua": "tshiluba",
}


class GroqError(Exception):
    """Erreur présentable à l'utilisateur lors d'un appel à l'assistant Groq."""


def redact_sensitive_data(text):
    text = re.sub(r"https?://\S+|www\.\S+", "[lien retiré]", text, flags=re.IGNORECASE)
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[adresse e-mail retirée]", text)
    text = re.sub(
        r"(?i)\b(?:code(?:\s+(?:pin|otp|secret|de vérification|de validation))?|pin|otp|mot de passe)"
        r"(?:\s+(?:est|is))?\s*[:=]?\s*[A-Z0-9]{4,10}\b",
        "[code secret retiré]",
        text,
    )
    text = re.sub(r"\+?\d[\d\s().-]{6,}\d", "[numéro retiré]", text)
    return text


def ask_groq(question, language):
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise GroqError("L'assistant IA n'est pas configuré. Ajoute GROQ_API_KEY au serveur.")

    language_name = LANGUAGE_NAMES.get(language, LANGUAGE_NAMES["fr"])
    payload = {
        "model": settings.GROQ_MODEL,
        "temperature": 0.2,
        "max_completion_tokens": 700,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu es l'assistant de prévention citoyenne d'USALAMA DÉFENSE en RDC. "
                    f"Réponds en {language_name}, avec des mots simples et des étapes courtes. "
                    "Aide à reconnaître les risques de fraude, sans prétendre être certain. "
                    "Ne demande et ne répète jamais un PIN, OTP, mot de passe ou donnée financière. "
                    "Pour une urgence, recommande de contacter l'opérateur par son canal officiel. "
                    "Ne donne pas de conseil pour commettre une fraude."
                ),
            },
            {"role": "user", "content": redact_sensitive_data(question)},
        ],
    }
    request = Request(
        GROQ_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        logger.warning("Groq assistant returned HTTP %s.", exc.code)
        raise GroqError(
            f"Le fournisseur Groq a refusé la requête (HTTP {exc.code}). Réessaie plus tard."
        ) from None
    except (URLError, TimeoutError):
        logger.warning("Groq assistant is unreachable.")
        raise GroqError("L'assistant Groq est momentanément inaccessible. Réessaie plus tard.") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.error("Groq assistant returned an invalid response.")
        raise GroqError("La réponse de l'assistant est invalide. Réessaie plus tard.") from None

    choices = result.get("choices") if isinstance(result, dict) else None
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        logger.error("Groq assistant response is missing choices.")
        raise GroqError("L'assistant n'a pas fourni de réponse exploitable.")
    message = choices[0].get("message")
    answer = message.get("content") if isinstance(message, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        logger.error("Groq assistant response is missing message content.")
        raise GroqError("L'assistant n'a pas fourni de réponse exploitable.")
    return answer.strip()
