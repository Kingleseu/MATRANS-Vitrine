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

Render fournit automatiquement `RENDER_EXTERNAL_HOSTNAME` pour son sous-domaine. La configuration ajoute cet hôte à `ALLOWED_HOSTS` et à la liste CSRF. Avec Supabase, employer l'URL PostgreSQL du pooler **Session** et activer TLS dans l'URL (`sslmode=require`) si nécessaire.

## Ordre du premier déploiement

1. Vérifier que le code préparé est dans le dépôt Git et que les fichiers `.sqlite3`, `.env`, les clés Google, les CV et le document FTP ne sont pas publiés.
   Inclure les migrations `vitrine_app` et les images de `static/vitrine/`, qui ne sont pas encore publiées par le seul fait de préparer ce dossier local.
   Le dépôt propre fixe Python sur la série 3.12 avec `.python-version`, compatible avec le Django utilisé.
2. Créer la base PostgreSQL et le disque persistant, puis le service Web avec les variables ci-dessus.
3. Lancer le déploiement. Le build installe uniquement les dépendances de la vitrine et collecte les fichiers statiques. Au démarrage, les migrations créent les tables et le contenu initial de la vitrine.
4. Créer un premier compte éditorial, distinct des comptes locaux. Sur un service Web payant, utiliser le Shell Render avec `python manage.py createsuperuser`. Le plan gratuit n'offre pas de Shell : depuis un terminal local, exécuter `python deploy/create_vitrine_admin.py`, puis saisir **l'External Database URL** de Render et le mot de passe souhaité. Le script masque les valeurs sensibles et ne les enregistre pas. Se connecter ensuite à `/gestion-vitrine/connexion/`.
5. Vérifier l'accueil, la page Activités, la carte, le studio, l'envoi d'un message de contact, la publication d'une image et le formulaire d'offre d'emploi. Vérifier qu'une image ajoutée reste disponible après un redéploiement et qu'un CV n'est téléchargeable que dans le studio connecté.
6. Faire une sauvegarde de la base et du disque avant de passer du sous-domaine de test au domaine officiel de MATRANS.

Les migrations fournissent un contenu initial, mais elles ne transportent pas automatiquement les modifications éditoriales faites dans la base SQLite locale. Si ces modifications doivent être conservées, exporter **seulement les contenus publics validés** et copier les images correspondantes vers le disque avant d'ouvrir le site au public. Ne pas transférer les messages, candidatures ou CV de test.

## Limites connues

- Cette préparation ne déploie rien automatiquement : elle ne fournit ni domaine MATRANS ni accès Render.
- Le document contenant FTP et MySQL ne sert pas à cette option Render. Les mots de passe qu'il contient doivent être remplacés avant toute utilisation de cet autre hébergement.
- Le formulaire de contact conserve les messages dans le studio, mais n'envoie pas encore d'e-mail.
- Le service de synchronisation Google Sheets de l'espace Rapports n'est pas inclus dans la vitrine.
- Les avertissements `check --deploy` sur HSTS des sous-domaines et le préchargement restent volontaires pendant les essais ; ils seront réévalués seulement quand le domaine officiel et ses sous-domaines seront confirmés.

Références : [déploiement Django sur Render](https://render.com/docs/deploy-django), [disques persistants Render](https://render.com/docs/disks), [liste de contrôle Django](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).
