"""Create the first vitrine editor from a local terminal on Render's Free plan.

The database URL and password are prompted without echo and are never saved.
Run only after the deployed service has completed its migrations.
"""

import getpass
import os
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def external_database_url(value):
    parsed = urlparse(value.strip())
    if parsed.scheme not in {'postgres', 'postgresql'} or not parsed.hostname or not parsed.password:
        raise ValueError('Utilisez l’URL PostgreSQL externe complète affichée par Render.')
    parameters = dict(parse_qsl(parsed.query, keep_blank_values=True))
    parameters['sslmode'] = 'require'
    return urlunparse(parsed._replace(query=urlencode(parameters)))


def main():
    print('Création du premier compte pour le studio MATRANS')
    print('Les valeurs secrètes saisies ici ne seront pas affichées ni enregistrées.')
    try:
        database_url = external_database_url(getpass.getpass('External Database URL de Render : '))
        username = input('Identifiant souhaité : ').strip()
        email = input('Adresse e-mail du compte : ').strip()
        password = getpass.getpass('Mot de passe : ')
        confirmation = getpass.getpass('Confirmer le mot de passe : ')
    except (EOFError, KeyboardInterrupt):
        print('\nOpération annulée.')
        return 1

    if not username or not email or password != confirmation:
        print('Identifiant, e-mail ou confirmation invalide.')
        return 1

    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings_vitrine_render'
    from django.core.management.utils import get_random_secret_key

    os.environ['DJANGO_SECRET_KEY'] = get_random_secret_key()
    os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost'
    os.environ['DATABASE_URL'] = database_url

    import django
    from django.contrib.auth import get_user_model
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email
    from django.db import DatabaseError

    django.setup()
    try:
        validate_email(email)
        validate_password(password)
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            print('Cet identifiant existe déjà. Aucun compte n’a été modifié.')
            return 1
        User.objects.create_superuser(username=username, email=email, password=password)
    except ValidationError as exc:
        print('Mot de passe refusé : ' + ' '.join(exc.messages))
        return 1
    except DatabaseError:
        print('Connexion à la base impossible. Vérifiez son URL externe et que les migrations Render sont terminées.')
        return 1
    finally:
        os.environ.pop('DATABASE_URL', None)
        os.environ.pop('DJANGO_SECRET_KEY', None)

    print('Compte créé. Connectez-vous à /gestion-vitrine/connexion/.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
