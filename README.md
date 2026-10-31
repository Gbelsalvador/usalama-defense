# USALAMA DÉFENSE

Application Django de prévention des arnaques, avec analyse locale des messages, bibliothèque de conseils et signalements anonymisés.

## Installation locale

Crée un fichier `.env` à la racine du projet pour les paramètres privés, par exemple :

```dotenv
GROQ_API_KEY=ta-cle-groq
GROQ_MODEL=openai/gpt-oss-20b
```

Le fichier `.env` est ignoré par Git. Une variable déjà définie dans l'environnement du système ou du serveur reste prioritaire sur celle du fichier.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver
```

Sous macOS/Linux, active l'environnement avec `source .venv/bin/activate` après sa création. Le site est disponible sur <http://127.0.0.1:8000/> et l'administration sur <http://127.0.0.1:8000/admin/>.

## Vérifications

```powershell
python manage.py check
python manage.py test
```

## Déploiement

Ne déploie pas avec la clé de développement. Configure les variables d'environnement `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS` (noms d'hôte séparés par des virgules) et `CSRF_TRUSTED_ORIGINS` (origines HTTPS séparées par des virgules). Le mode production active les cookies sécurisés, HSTS et la redirection HTTPS par défaut. N'active `SECURE_HSTS_INCLUDE_SUBDOMAINS=1` ou `SECURE_HSTS_PRELOAD=1` que si tous les sous-domaines concernés sont prêts pour HTTPS. Si TLS est terminé par un proxy de confiance, active `USE_X_FORWARDED_PROTO=1` et configure le proxy pour écraser l'en-tête `X-Forwarded-Proto`. Vérifie ensuite avec `python manage.py check --deploy`.

La configuration fournie utilise SQLite ; choisis une base de données adaptée à ton hébergeur avant une mise en production à plusieurs utilisateurs. Configure aussi la collecte et le service des fichiers statiques (`python manage.py collectstatic`).

## Fonctionnement et langues

- L'analyse des messages se fait dans le navigateur (`static/js/analyzer.js`) ; le texte analysé n'est pas envoyé au serveur. L'historique reste dans le stockage local du navigateur.
- L'assistant est une fonction distincte, facultative et connectée : il envoie la description à Groq après consentement explicite. Les liens, e-mails, numéros et codes secrets reconnus sont masqués avant l'envoi. Le serveur ne sauvegarde pas les échanges. L'assistant ne doit jamais recevoir de PIN, OTP, mot de passe ou donnée financière.
- Configure `GROQ_API_KEY` dans l'environnement du serveur pour activer l'assistant. Le modèle par défaut est `openai/gpt-oss-20b`; `GROQ_MODEL` permet de choisir un autre modèle GPT-OSS disponible sur ton compte Groq. Sans clé, l'assistant affiche une erreur de configuration et ne prétend pas fonctionner.
- Les pages d'accueil, guides, conseils d'urgence, règles d'analyse et fichiers statiques consultés peuvent être mis en cache dans le navigateur. Les listes de guides et de conseils proposent un bouton d'enregistrement hors connexion. L'assistant et les signalements restent en ligne.
- Les signalements sont facultatifs. Les numéros, liens et adresses e-mail sont masqués avant l'enregistrement ; ne transmets jamais un PIN, un OTP ou un mot de passe.
- Les contenus de la bibliothèque sont des objets JSON par langue, par exemple `{"fr": "...", "ln": "..."}`. Une traduction est affichée uniquement si elle est incluse dans `langues_validees`.
- La commande `seed` fournit des exemples en français. Les traductions de contenu doivent être ajoutées et validées avant d'activer une langue dans l'administration.
- Pour traduire l'interface, utilise `python manage.py makemessages -l ln` puis `python manage.py compilemessages` (nécessite GNU gettext).

La bibliothèque de démonstration est chargée avec `python manage.py seed`. Elle contient 12 fiches et 9 situations d'urgence en français. Les traductions Lingala, Swahili, Kikongo ya Leta et Tshiluba ne doivent être activées qu'après validation par des locuteurs natifs.
