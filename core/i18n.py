from django.utils.translation import get_language

def tr(value, lang=None, validated=None):
    """Renvoie la valeur d'un champ JSON {"fr": ..., "ln": ...}.
    Retombe sur le français si la langue n'existe pas ou n'est pas validée."""
    lang = lang or get_language() or "fr"
    if not isinstance(value, dict):
        return value
    if validated is not None and lang not in validated:
        lang = "fr"
    return value.get(lang) or value.get("fr", "")
