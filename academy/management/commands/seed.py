from django.core.management.base import BaseCommand
from academy.models import Scam, Situation
from analyzer.models import Rule

def fr(x): return {"fr": x}

RULES = [
 ("pin_otp", r"code (pin|otp|secret)|\botp\b|\bpin\b|mot de passe", 4,
  "Le message parle d'un code PIN, d'un OTP ou d'un mot de passe. Un vrai agent ou opérateur ne les demande jamais.",
  "Ne donne jamais ton code PIN, ton OTP ou ton mot de passe, à personne."),
 ("urgence", r"urgent|immediatement|tout de suite|dans les \d+ ?(minutes|heures)|dernier avertissement|sinon (votre|ton) compte", 2,
  "Le message te met la pression pour agir vite. Les arnaqueurs veulent t'empêcher de réfléchir.",
  "Prends ton temps. Une vraie urgence peut toujours être vérifiée auprès de ton opérateur."),
 ("blocage", r"compte (est |sera |a ete )?(bloque|suspendu|desactive)|debloquer", 3,
  "Le message annonce un blocage de compte, un prétexte classique pour obtenir tes codes.",
  "Ne réponds pas. Contacte ton opérateur avec son numéro officiel ou va dans une de ses agences."),
 ("remboursement", r"rembours|par erreur|erreur de (transfert|depot|envoi)|renvoy\w+ (moi )?l'argent", 3,
  "Le message parle d'un remboursement ou d'un envoi par erreur, souvent utilisé pour te faire envoyer de l'argent.",
  "Ne renvoie pas d'argent. Vérifie ton solde par le menu officiel de ton opérateur, pas par un message."),
 ("usurpation", r"je (suis|travaille).{0,30}(orange|airtel|vodacom|m-?pesa|africell|banque)|service client|equipe technique", 3,
  "La personne dit appartenir à un opérateur ou à une banque. Cela s'invente facilement.",
  "Raccroche ou ignore, puis appelle toi-même le numéro officiel de l'opérateur."),
 ("gain", r"felicitations|vous avez gagne|tu as gagne|tirage au sort|loterie|gagnant", 3,
  "Le message promet un gain ou un cadeau que tu n'as pas demandé.",
  "Un gain réel ne demande jamais de payer ni de donner un code. Ignore le message."),
 ("demande_argent", r"(envoy|transf|depos)\w+ .{0,25}(argent|francs|fc\b|usd|dollars|\$)", 2,
  "Le message demande d'envoyer ou de transférer de l'argent.",
  "N'envoie rien avant d'avoir joint la personne par un autre moyen que tu connais."),
 ("faux_depot", r"vous avez recu .{0,30}(fc|usd|\$)|capture d'ecran", 2,
  "Le message ressemble à une fausse confirmation de dépôt.",
  "Vérifie le dépôt dans ton solde officiel avant de remettre un produit ou de l'argent."),
]

SCAMS = [
 ("faux-agent", "Le faux agent Mobile Money",
  "Une personne se fait passer pour un agent ou un employé de l'opérateur afin d'obtenir ton code ou ton argent.",
  "Quelqu'un t'appelle : « Je suis de chez Orange, ton compte va être bloqué. Donne-moi ton code pour le sauver. »",
  ["Il t'appelle ou t'écrit sans que tu aies rien demandé.", "Il te demande ton code PIN ou un code reçu par SMS.", "Il te presse de répondre vite."],
  ["Donner un code « pour vérifier »", "Rester au téléphone pendant que tu fais des opérations"],
  ["Raccroche immédiatement.", "Rappelle ton opérateur par son numéro officiel.", "Ne partage jamais ton PIN ni ton OTP."]),
 ("faux-depot", "Le faux message de dépôt",
  "Tu reçois un SMS imitant une confirmation de dépôt pour te faire livrer un produit ou rendre de la monnaie.",
  "Un client te montre un SMS « Vous avez reçu 50 000 FC » et te demande de lui rendre la différence.",
  ["Le SMS n'arrive pas du service officiel.", "Ton solde n'a pas changé.", "On te demande de rendre de l'argent tout de suite."],
  ["Te fier à une capture d'écran ou à un SMS seul"],
  ["Vérifie toujours ton solde via le menu officiel.", "Attends la confirmation réelle avant de remettre quoi que ce soit."]),
 ("faux-remboursement", "Le faux remboursement",
  "Une personne dit s'être trompée en t'envoyant de l'argent et te demande de le renvoyer, ou de donner un code pour l'annuler.",
  "« Je t'ai envoyé de l'argent par erreur, renvoie-le-moi vite, c'est pour l'hôpital. »",
  ["L'histoire est émouvante et pressante.", "Aucun dépôt réel n'apparaît sur ton compte."],
  ["Renvoyer l'argent sans avoir vérifié ton solde"],
  ["Vérifie ton solde officiel.", "Si un vrai dépôt existe, passe par ton opérateur pour l'annuler."]),
 ("lien-phishing", "Le lien piégé",
  "Un lien envoyé par SMS ou WhatsApp mène vers un faux site qui copie tes informations.",
  "« Votre compte est suspendu. Cliquez ici pour le réactiver : http://... »",
  ["Le lien est raccourci ou l'adresse est étrange.", "Le message te demande de te connecter ou de saisir un code."],
  ["Cliquer puis saisir son numéro, son PIN ou un code"],
  ["Ne clique pas.", "Ouvre toi-même l'application ou le menu officiel."]),
 ("faux-concours", "Le faux concours ou gain",
  "On t'annonce un gain pour te faire payer des frais ou donner des informations.",
  "« Félicitations ! Vous avez gagné un téléphone. Envoyez 5 000 FC de frais de livraison. »",
  ["Tu n'as participé à aucun concours.", "On demande de l'argent ou un code pour recevoir le gain."],
  ["Payer des frais pour recevoir un gain"],
  ["Ignore le message.", "Prévenir ton entourage qui pourrait recevoir le même."]),
 ("usurpation-whatsapp", "L'usurpation sur WhatsApp",
  "Un faux compte, ou un compte piraté, imite un proche et demande de l'argent en urgence.",
  "Un message d'un « nouveau numéro » de ton frère : « Dépanne-moi, je te rembourse ce soir. »",
  ["Nouveau numéro, photo copiée.", "Demande d'argent urgente et pas d'appel possible."],
  ["Envoyer de l'argent sans avoir entendu la voix de la personne"],
  ["Appelle l'ancien numéro de ton proche.", "Pose une question que seul le vrai proche connaît."]),
]

SITUATIONS = [
 ("pin-communique", "J'ai communiqué mon code PIN",
  ["Change immédiatement ton code PIN depuis le menu officiel.", "Appelle ton opérateur avec son numéro officiel ou rends-toi dans une agence pour signaler le problème.", "Ne fais plus d'opération avec la personne.", "Vérifie les dernières transactions de ton compte."]),
 ("lien-clique", "J'ai cliqué sur un lien suspect",
  ["Ne saisis rien. Ferme la page.", "Si tu as saisi un code ou un mot de passe, change-le tout de suite.", "Préviens ton opérateur.", "Supprime le message."]),
 ("faux-depot-recu", "J'ai reçu un faux message de dépôt",
  ["Ne remets rien et ne rends pas de monnaie.", "Vérifie ton solde par le menu officiel.", "Garde le message pour le signaler."]),
 ("argent-envoye", "J'ai envoyé de l'argent à un inconnu",
  ["Contacte ton opérateur au plus vite avec les détails de la transaction.", "Garde le numéro, l'heure et le montant.", "Ne paie aucun « frais pour récupérer » ton argent.", "Signale-le aux autorités compétentes."]),
 ("identite-utilisee", "Quelqu'un utilise mon identité",
  ["Préviens tes proches et ton opérateur.", "Change tes mots de passe et ton code PIN.", "Garde des preuves : captures et numéros.", "Dépose une plainte si nécessaire."]),
 ("compte-compromis", "Je pense que mon compte est compromis",
  ["Change ton code PIN depuis le menu officiel.", "Contacte ton opérateur depuis son numéro officiel.", "Vérifie les transactions récentes.", "Ne communique aucun code à qui que ce soit."]),
]

class Command(BaseCommand):
    help = "Charge les règles, fiches et situations d'exemple (français)."
    def handle(self, *a, **k):
        for code, pat, poids, expl, cons in RULES:
            Rule.objects.update_or_create(code=code, defaults=dict(patterns={"fr": [pat]}, poids=poids, explication=fr(expl), conseil=fr(cons)))
        for slug, nom, ex, exemple, signes, err, prot in SCAMS:
            Scam.objects.update_or_create(slug=slug, defaults=dict(nom=fr(nom), explication=fr(ex), exemple=fr(exemple),
                signes=fr(signes), erreurs=fr(err), protections=fr(prot), langues_validees=["fr"]))
        for slug, titre, actions in SITUATIONS:
            Situation.objects.update_or_create(slug=slug, defaults=dict(titre=fr(titre), actions=fr(actions), langues_validees=["fr"]))
        self.stdout.write(self.style.SUCCESS("Données d'exemple chargées."))
