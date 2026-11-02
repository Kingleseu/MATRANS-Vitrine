"""Standalone production settings for the public MATRANS showcase on Render."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip()
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY est obligatoire sur Render.')

DEBUG = False
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
ALLOWED_HOSTS = list(dict.fromkeys(
    host for host in (
        _render_host,
        *(part.strip() for part in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')),
    ) if host
))
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('Définissez DJANGO_ALLOWED_HOSTS ou RENDER_EXTERNAL_HOSTNAME.')
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(
    [f'https://{host}' for host in ALLOWED_HOSTS if '*' not in host]
    + [origin.strip().rstrip('/') for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'vitrine_app',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'core.vitrine_urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'core.wsgi.application'

_database_url = os.environ.get('DATABASE_URL', '').strip()
if not _database_url:
    raise ImproperlyConfigured('DATABASE_URL PostgreSQL est obligatoire sur Render.')
DATABASES = {'default': dj_database_url.parse(
    _database_url, conn_max_age=300, conn_health_checks=True,
)}
if DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
    raise ImproperlyConfigured('La vitrine Render requiert une base PostgreSQL persistante.')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LOGIN_URL = '/gestion-vitrine/connexion/'
LOGIN_REDIRECT_URL = '/gestion-vitrine/'
LOGOUT_REDIRECT_URL = LOGIN_URL
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Mount a persistent Render disk at /var/data before accepting uploads.
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', '/var/data/media'))
PRIVATE_MEDIA_ROOT = Path(os.environ.get('PRIVATE_MEDIA_ROOT', '/var/data/private_media'))

# Optional contact notifications and replies through Brevo's HTTPS API.
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '').strip()
CONTACT_FROM_EMAIL = os.environ.get('CONTACT_FROM_EMAIL', '').strip()
CONTACT_INBOX_EMAIL = os.environ.get('CONTACT_INBOX_EMAIL', 'contact@matrans-rdc.com').strip()
VITRINE_SETUP_TOKEN = os.environ.get('VITRINE_SETUP_TOKEN', '').strip()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
