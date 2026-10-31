import logging
import re

from django.conf import settings
from groq import APIConnectionError, APIStatusError, Groq

logger = logging.getLogger(__name__)

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
    messages = [
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
    ]

    try:
        with Groq(api_key=api_key, timeout=30.0, max_retries=1) as client:
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.2,
                max_completion_tokens=700,
            )
    except APIStatusError as exc:
        logger.warning("Groq assistant returned HTTP %s.", exc.status_code)
        raise GroqError(
            f"Le fournisseur Groq a refusé la requête (HTTP {exc.status_code}). Réessaie plus tard."
        ) from None
    except APIConnectionError:
        logger.warning("Groq assistant is unreachable.")
        raise GroqError("L'assistant Groq est momentanément inaccessible. Réessaie plus tard.") from None

    if not completion.choices:
        logger.error("Groq assistant response is missing choices.")
        raise GroqError("L'assistant n'a pas fourni de réponse exploitable.")
    answer = completion.choices[0].message.content
    if not isinstance(answer, str) or not answer.strip():
        logger.error("Groq assistant response is missing message content.")
        raise GroqError("L'assistant n'a pas fourni de réponse exploitable.")
    return answer.strip()
