# USALAMA DÉFENSE (Django, web)

    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed                # règles, fiches et situations d'exemple (français)
    python manage.py createsuperuser
    python manage.py runserver

Site : http://127.0.0.1:8000/  ·  Administration : /admin/

- L'analyse des messages se fait dans le navigateur (static/js/analyzer.js) ; le texte n'est pas envoyé au serveur.
- Les contenus sont saisis dans l'admin sous forme {"fr": "...", "ln": "..."} ; une langue n'est affichée que si elle figure dans « langues_validees ».
- Textes d'interface : `python manage.py makemessages -l ln` puis `compilemessages` (nécessite gettext).
