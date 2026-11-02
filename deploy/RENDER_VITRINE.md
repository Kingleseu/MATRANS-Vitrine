# Préparer et héberger uniquement la vitrine MATRANS sur Render

Cette configuration publie `/` et `/gestion-vitrine/`. Elle n'expose ni les routes EPI, ni les rapports des CD, ni `/admin/`. Le développement local conserve `core.settings` et ses bases SQLite ; Render utilise `core.settings_vitrine_render` et une base PostgreSQL distincte.

## Dépôt GitHub propre

L'historique du dépôt Git actuel contient d'anciennes bases SQLite. Une branche créée depuis cet historique les conserverait dans les anciens commits. Pour la vitrine, utiliser le dossier `tmp/vitrine_render_export` préparé par `scripts/prepare_vitrine_render_export.py` : c'est un **nouveau dépôt Git indépendant**, sans bases de données ni fichiers EPI ou Rapports.

Créer sur GitHub un nouveau dépôt **privé**, sans README ni licence ni `.gitignore` générés par GitHub. Depuis le dossier d'export, ajouter l'URL exacte de ce nouveau dépôt comme `origin`, puis pousser `main`. Ne pas utiliser l'URL du dépôt historique `MATRANS-Logistique-Web` pour cette copie.

## Ce qu'il faut créer dans Render

1. Une base **PostgreSQL persistante** dédiée à la vitrine (Render Postgres, ou une base Supabase séparée). Conserver son URL de connexion dans les variables secrètes Render, jamais dans le dépôt.
2. Un service **Web Python** lié au dépôt Git et à la branche contenant cette préparation.
3. Un **disque persistant** monté sur `/var/data` pour les images ajoutées dans le studio et les CV privés. Sur Render, le disque d'un service Web est une option payante. Sans disque, les fichiers téléversés peuvent disparaître après redémarrage ou redéploiement : ne pas ouvrir les formulaires publics dans cette configuration.

### Réglages du service Web

| Champ Render | Valeur |
| --- | --- |
| Root Directory | laisser vide |
| Language | Python 3 |
| Build Command | `bash deploy/render_vitrine_build.sh` |
| Start Command | `bash deploy/render_vitrine_start.sh` |
| Health Check Path | `/` |

Variables d'environnement :

| Nom | Valeur |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `core.settings_vitrine_render` |
| `DJANGO_SECRET_KEY` | valeur longue aléatoire générée dans Render |
| `DATABASE_URL` | URL PostgreSQL de la base dédiée |
| `MEDIA_ROOT` | `/var/data/media` |
| `PRIVATE_MEDIA_ROOT` | `/var/data/private_media` |
| `DJANGO_ALLOWED_HOSTS` | facultatif ; ajouter le domaine personnalisé une fois connu |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | facultatif ; origines HTTPS personnalisées supplémentaires |
| `BREVO_API_KEY` | clé API Brevo, une fois le domaine expéditeur authentifié |
| `CONTACT_FROM_EMAIL` | adresse expéditrice vérifiée dans Brevo ; utiliser `contact@matrans-rdc.com` seulement après sa validation dans Brevo |
| `CONTACT_INBOX_EMAIL` | `contact@matrans-rdc.com` ; remplacer toute ancienne valeur déjà définie sur Render |
| `VITRINE_SETUP_TOKEN` | code aléatoire d'au moins 24 caractères, à définir temporairement pour créer le premier accès depuis le site |

Render fournit automatiquement `RENDER_EXTERNAL_HOSTNAME` pour son sous-domaine. La configuration ajoute cet hôte à `ALLOWED_HOSTS` et à la liste CSRF. Avec Supabase, employer l'URL PostgreSQL du pooler **Session** et activer TLS dans l'URL (`sslmode=require`) si nécessaire.

## Ordre du premier déploiement

1. Vérifier que le code préparé est dans le dépôt Git et que les fichiers `.sqlite3`, `.env`, les clés Google, les CV et le document FTP ne sont pas publiés.
   Inclure les migrations `vitrine_app` et les images de `static/vitrine/`, qui ne sont pas encore publiées par le seul fait de préparer ce dossier local.
   Le dépôt propre fixe Python sur la série 3.12 avec `.python-version`, compatible avec le Django utilisé.
2. Créer la base PostgreSQL et le disque persistant, puis le service Web avec les variables ci-dessus.
3. Lancer le déploiement. Le build installe uniquement les dépendances de la vitrine et collecte les fichiers statiques. Au démarrage, les migrations créent les tables et le contenu initial de la vitrine.
4. Créer un premier compte, distinct des comptes locaux : l'identifiant `ebenn-vitrine` créé sur le poste de développement n'est pas transféré par Git. Dans l'onglet **Environment** du service Render, définir temporairement `VITRINE_SETUP_TOKEN` avec un code aléatoire d'au moins 24 caractères, puis attendre le redéploiement. Ouvrir `/gestion-vitrine/connexion/`, cliquer sur **Créer le premier accès** et remplir le formulaire avec ce code, un identifiant, une adresse e-mail et un mot de passe personnel. Le formulaire se ferme dès que le premier administrateur existe. Supprimer ensuite `VITRINE_SETUP_TOKEN` des variables Render. Depuis **Comptes du studio**, l'administrateur peut créer des accès éditeurs sans nouvelle configuration. Ne jamais placer le code dans Git ni l'envoyer par message.
   Si ce parcours n'est pas possible, le script `python deploy/create_vitrine_admin.py` reste disponible depuis un terminal local avec l'URL PostgreSQL externe ; sur un service payant, le Shell Render peut aussi lancer `python manage.py createsuperuser`.
5. Vérifier l'accueil, la page Activités, la carte, le studio, l'envoi d'un message de contact, la publication d'une image et le formulaire d'offre d'emploi. Vérifier qu'une image ajoutée reste disponible après un redéploiement et qu'un CV n'est téléchargeable que dans le studio connecté.
6. Faire une sauvegarde de la base et du disque avant de passer du sous-domaine de test au domaine officiel de MATRANS.

Les migrations fournissent un contenu initial, mais elles ne transportent pas automatiquement les modifications éditoriales faites dans la base SQLite locale. Si ces modifications doivent être conservées, exporter **seulement les contenus publics validés** et copier les images correspondantes vers le disque avant d'ouvrir le site au public. Ne pas transférer les messages, candidatures ou CV de test.

## Limites connues

- Cette préparation ne déploie rien automatiquement : elle ne fournit ni domaine MATRANS ni accès Render.
- Le document contenant FTP et MySQL ne sert pas à cette option Render. Les mots de passe qu'il contient doivent être remplacés avant toute utilisation de cet autre hébergement.
- Sur Render Free, les ports SMTP 25, 465 et 587 sont bloqués. Pour recevoir les notifications et répondre depuis le studio, créer un compte Brevo, vérifier l'adresse expéditrice et authentifier son domaine, puis renseigner `BREVO_API_KEY`, `CONTACT_FROM_EMAIL` et `CONTACT_INBOX_EMAIL` dans les variables Render. Ne jamais placer la clé dans GitHub ou dans une capture. L'application envoie les courriels par l'API HTTPS Brevo ; les messages restent en base même si l'envoi échoue. Le studio indique alors « Échec » et n'affiche une réponse comme envoyée qu'après confirmation de l'API.
- Tant que ces trois variables ne sont pas configurées, les messages sont enregistrés et lisibles dans le studio, mais aucune notification ni réponse par e-mail n'est envoyée. Tester l'envoi avec une adresse personnelle avant de communiquer le formulaire aux partenaires.
- Logo BRACONGO : fichier statique provenant de la [page officielle BRACONGO](https://bracongo.cd/) ; remplacer dans le studio si une version officielle plus nette est fournie.
- Le service de synchronisation Google Sheets de l'espace Rapports n'est pas inclus dans la vitrine.
- Les avertissements `check --deploy` sur HSTS des sous-domaines et le préchargement restent volontaires pendant les essais ; ils seront réévalués seulement quand le domaine officiel et ses sous-domaines seront confirmés.

Références : [déploiement Django sur Render](https://render.com/docs/deploy-django), [disques persistants Render](https://render.com/docs/disks), [liste de contrôle Django](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).
