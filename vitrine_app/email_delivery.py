"""Transactional email through Brevo's HTTPS API.

Render Free blocks outbound SMTP ports, so the public site uses HTTPS when an
API key has been configured. Contact messages remain in PostgreSQL either way.
"""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)
BREVO_ENDPOINT = 'https://api.brevo.com/v3/smtp/email'


class MailNotConfigured(Exception):
    pass


class MailDeliveryError(Exception):
    pass


def mail_ready():
    return bool(settings.BREVO_API_KEY and settings.CONTACT_FROM_EMAIL)


def send_email(*, recipient, subject, body, reply_to=None):
    if not mail_ready():
        raise MailNotConfigured('La messagerie du site n’est pas encore configurée.')
    payload = {
        'sender': {'email': settings.CONTACT_FROM_EMAIL, 'name': 'MATRANS'},
        'to': [{'email': recipient}],
        'subject': ' '.join(subject.split())[:180],
        'textContent': body,
    }
    if reply_to:
        payload['replyTo'] = {'email': reply_to}
    request = Request(
        BREVO_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=12) as response:
            if response.status != 201:
                raise MailDeliveryError('Le service de messagerie n’a pas confirmé l’envoi.')
    except (HTTPError, URLError, TimeoutError) as exc:
        logger.warning('Échec de livraison Brevo (%s)', getattr(exc, 'code', type(exc).__name__))
        raise MailDeliveryError('Le message n’a pas pu être envoyé par e-mail.') from exc


def notify_contact(item):
    body = (
        f'Nouveau message reçu depuis la vitrine MATRANS.\n\n'
        f'Nom : {item.nom}\nE-mail : {item.email}\n'
        f'Téléphone : {item.telephone or "Non indiqué"}\nSujet : {item.sujet}\n\n'
        f'Message :\n{item.message}\n\n'
        f'Le message est aussi disponible dans le studio MATRANS.'
    )
    send_email(
        recipient=settings.CONTACT_INBOX_EMAIL,
        subject=f'Nouveau contact · {item.sujet}',
        body=body,
        reply_to=item.email,
    )


def send_contact_reply(item, text):
    send_email(
        recipient=item.email,
        subject=f'Réponse de MATRANS · {item.sujet}',
        body=text,
        reply_to=settings.CONTACT_INBOX_EMAIL,
    )
