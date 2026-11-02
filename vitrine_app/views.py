from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CandidatureForm, ContactForm
from .email_delivery import MailDeliveryError, MailNotConfigured, notify_contact
from .map_geometry import MAP_HEIGHT, MAP_WIDTH, project
from .models import Activite, CentreVitrine, Evenement, MembreEquipe, OffreEmploi, Partenaire, SiteContent


def _site():
    return SiteContent.objects.first() or SiteContent()


def _context(*, site=None, **extra):
    site = site or _site()
    return {'site': site, **extra}


def _require_page(site, field):
    if not getattr(site, field):
        raise Http404


def _open_offers():
    return OffreEmploi.objects.filter(est_active=True).filter(
        Q(date_limite__isnull=True) | Q(date_limite__gte=timezone.localdate())
    )

def _map_data():
    centres = list(CentreVitrine.objects.filter(publie=True))
    zones_by_name = {}
    centres_sans_point = []
    for centre in centres:
        if centre.latitude is None or centre.longitude is None:
            centres_sans_point.append(centre)
            continue
        key = centre.zone_carte or centre.code
        if key not in zones_by_name:
            zones_by_name[key] = {
                'id': f'zone-{len(zones_by_name) + 1}',
                'nom': centre.zone_carte or centre.ville or centre.nom,
                'x': 0,
                'y': 0,
                'centres': [],
            }
        x, y = project(centre.longitude, centre.latitude)
        zone = zones_by_name[key]
        zone['centres'].append(centre)
        zone['x'] += x / MAP_WIDTH * 100
        zone['y'] += y / MAP_HEIGHT * 100
    for zone in zones_by_name.values():
        zone['x'] = round(zone['x'] / len(zone['centres']), 3)
        zone['y'] = round(zone['y'] / len(zone['centres']), 3)
    return {
        'zones': list(zones_by_name.values()), 'centres_total': len(centres),
        'centres_sans_point': centres_sans_point,
        'provinces_total': len({centre.province.strip().casefold() for centre in centres if centre.province.strip()}),
    }


def home(request):
    return render(request, 'vitrine/home.html', _context(
        activites=Activite.objects.filter(publiee=True)[:4],
        partenaires=Partenaire.objects.filter(publie=True),
        offres=_open_offers()[:3],
        evenements=Evenement.objects.filter(publie=True)[:3],
        **_map_data(),
    ))


def a_propos(request):
    site = _site()
    _require_page(site, 'page_about_visible')
    membres = MembreEquipe.objects.filter(publie=True) if site.show_team else MembreEquipe.objects.none()
    return render(request, 'vitrine/a_propos.html', {'site': site, 'membres': membres})

def activites(request):
    site = _site()
    _require_page(site, 'page_activities_visible')
    return render(request, 'vitrine/activites.html', _context(site=site,
        activites=Activite.objects.filter(publiee=True),
        **_map_data(),
    ))


def partenaires(request):
    site = _site()
    _require_page(site, 'page_partners_visible')
    return render(request, 'vitrine/partenaires.html', _context(site=site,
        partenaires=Partenaire.objects.filter(publie=True)
    ))

def carrieres(request):
    site = _site()
    _require_page(site, 'page_careers_visible')
    return render(request, 'vitrine/carrieres.html', _context(site=site, offres=_open_offers()))

def offre_detail(request, pk):
    site = _site()
    _require_page(site, 'page_careers_visible')
    offre = get_object_or_404(_open_offers().prefetch_related('questions'), pk=pk)
    form = CandidatureForm(request.POST or None, request.FILES or None, offre=offre)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Votre candidature a été reçue. Merci pour votre intérêt.')
        return redirect('carrieres')
    return render(request, 'vitrine/offre_detail.html', _context(site=site, offre=offre, form=form))


def evenements(request):
    site = _site()
    _require_page(site, 'page_events_visible')
    return render(request, 'vitrine/evenements.html', _context(site=site,
        evenements=Evenement.objects.filter(publie=True)
    ))


def evenement_detail(request, pk):
    site = _site()
    _require_page(site, 'page_events_visible')
    evenement = get_object_or_404(Evenement, pk=pk, publie=True)
    return render(request, 'vitrine/evenement_detail.html', _context(site=site, evenement=evenement))


def contact(request):
    site = _site()
    _require_page(site, 'page_contact_visible')
    initial = {'sujet': 'Proposition de partenariat'} if request.GET.get('objet') == 'partenariat' else None
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        try:
            notify_contact(item)
        except MailNotConfigured:
            pass
        except MailDeliveryError:
            item.notification_status = 'erreur'
            item.save(update_fields=['notification_status'])
        else:
            item.notification_status = 'envoye'
            item.save(update_fields=['notification_status'])
        messages.success(request, 'Votre message a été reçu. Nous reviendrons vers vous.')
        return redirect('contact')
    return render(request, 'vitrine/contact.html', _context(site=site, form=form))
