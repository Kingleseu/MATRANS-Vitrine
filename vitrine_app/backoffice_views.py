from functools import wraps
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.db import connections, router, transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from .email_delivery import MailDeliveryError, MailNotConfigured, mail_ready, send_contact_reply
from .forms import (
    ActiviteForm, CentreVitrineForm, EvenementForm, MembreEquipeForm, OffreEmploiForm,
    OffreQuestionForm, PageVisibilityForm, PartenaireForm, SiteContentForm, ContactReplyForm,
    InitialStudioAccountForm, StudioAccountForm,
)
from .models import (
    Activite, Candidature, CentreVitrine, ContactMessage, ContactReply, Evenement, MembreEquipe,
    OffreEmploi, OffreQuestion, Partenaire, SiteContent,
)


SECTIONS = {
    'activites': (Activite, ActiviteForm, 'Activités', 'Décrivez les services réellement proposés.'),
    'centres': (CentreVitrine, CentreVitrineForm, 'Sites sur la carte', "Renseignez l'activité, corrigez les positions indicatives et publiez les fiches visibles sur la carte de la RDC."),
    'partenaires': (Partenaire, PartenaireForm, 'Partenaires', 'Publiez uniquement les collaborations autorisées.'),
    'offres': (OffreEmploi, OffreEmploiForm, "Offres d'emploi", 'Créez une offre, puis adaptez son formulaire.'),
    'evenements': (Evenement, EvenementForm, 'Événements', 'Préparez puis publiez vos actualités et événements.'),
    'equipe': (MembreEquipe, MembreEquipeForm, 'Équipe', 'Chaque profil reste masqué tant que vous ne le publiez pas.'),
}


def initial_account_available():
    token = settings.VITRINE_SETUP_TOKEN
    return len(token) >= 24 and not get_user_model().objects.filter(is_superuser=True).exists()


class StudioLoginView(LoginView):
    template_name = 'vitrine/backoffice/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_account_available'] = initial_account_available()
        return context


@sensitive_post_parameters('access_code', 'password1', 'password2')
@never_cache
def initial_account(request):
    if not initial_account_available():
        raise Http404
    form = InitialStudioAccountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        supplied = form.cleaned_data['access_code'].encode('utf-8')
        expected = settings.VITRINE_SETUP_TOKEN.encode('utf-8')
        if not secrets.compare_digest(supplied, expected):
            form.add_error('access_code', "Code d'installation invalide.")
        else:
            User = get_user_model()
            db = router.db_for_write(User)
            with transaction.atomic(using=db):
                if connections[db].vendor == 'postgresql':
                    with connections[db].cursor() as cursor:
                        cursor.execute('SELECT pg_advisory_xact_lock(%s)', [20261102])
                if User.objects.using(db).filter(is_superuser=True).exists():
                    raise Http404
                user = User.objects.db_manager(db).create_superuser(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('vitrine_admin:dashboard')
    return render(request, 'vitrine/backoffice/initial_account.html', {'form': form})


def editor_required(view):
    @wraps(view)
    @login_required(login_url='vitrine_admin:connexion')
    def wrapped(request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or user.groups.filter(name='Editeurs vitrine').exists()):
            return HttpResponseForbidden('Cet espace est réservé aux éditeurs de la vitrine.')
        return view(request, *args, **kwargs)
    return wrapped


def _layout(**extra):
    return {'backoffice_sections': [(key, config[2]) for key, config in SECTIONS.items()], **extra}


@editor_required
def accounts_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Seul un administrateur peut gérer les accès.')
    User = get_user_model()
    users = User.objects.filter(
        Q(is_superuser=True) | Q(groups__name='Editeurs vitrine')
    ).distinct().order_by('username')
    return render(request, 'vitrine/backoffice/accounts.html', _layout(users=users))


@editor_required
def account_create(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Seul un administrateur peut créer des accès.')
    form = StudioAccountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='Editeurs vitrine')
        user.groups.add(group)
        messages.success(request, 'Le compte éditeur a été créé.')
        return redirect('vitrine_admin:accounts')
    return render(request, 'vitrine/backoffice/account_form.html', _layout(form=form))


@editor_required
def dashboard(request):
    counts = {
        'activites': Activite.objects.count(),
        'centres': CentreVitrine.objects.filter(publie=True).count(),
        'partenaires': Partenaire.objects.filter(publie=True).count(),
        'offres': OffreEmploi.objects.filter(est_active=True).count(),
        'evenements': Evenement.objects.filter(publie=True).count(),
        'candidatures': Candidature.objects.count(),
        'messages': ContactMessage.objects.filter(traite=False).count(),
    }
    return render(request, 'vitrine/backoffice/dashboard.html', _layout(counts=counts))


@editor_required
def site_content(request):
    instance = SiteContent.objects.first() or SiteContent(pk=1)
    form = SiteContentForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La présentation du site a été enregistrée.')
        return redirect('vitrine_admin:site_content')
    return render(request, 'vitrine/backoffice/form.html', _layout(
        form=form, title='Présentation & coordonnées', intro='Modifiez les textes, les photos, les chiffres clés et leur source avant publication.',
        return_url=reverse('vitrine_admin:dashboard'),
    ))


@editor_required
def page_visibility(request):
    instance = SiteContent.objects.first() or SiteContent(pk=1)
    form = PageVisibilityForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La visibilité des pages a été mise à jour.')
        return redirect('vitrine_admin:page_visibility')
    return render(request, 'vitrine/backoffice/page_visibility.html', _layout(form=form))


@editor_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Votre mot de passe a été modifié.')
        return redirect('vitrine_admin:dashboard')
    return render(request, 'vitrine/backoffice/form.html', _layout(
        form=form, title='Changer mon mot de passe',
        intro='Choisissez un mot de passe personnel pour votre compte du studio.',
        return_url=reverse('vitrine_admin:dashboard'),
    ))


@editor_required
def section_list(request, section):
    config = SECTIONS.get(section)
    if config is None:
        raise Http404
    model, _, title, intro = config
    return render(request, 'vitrine/backoffice/list.html', _layout(
        section=section, title=title, intro=intro, items=model.objects.all(),
    ))


@editor_required
def section_edit(request, section, pk=None):
    config = SECTIONS.get(section)
    if config is None:
        raise Http404
    model, form_class, title, intro = config
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        saved = form.save()
        messages.success(request, 'Les modifications ont été enregistrées.')
        if section == 'offres':
            return redirect('vitrine_admin:section_edit', section=section, pk=saved.pk)
        return redirect('vitrine_admin:section_list', section=section)
    return render(request, 'vitrine/backoffice/form.html', _layout(
        section=section, title=f'{title} · {"Modifier" if instance else "Ajouter"}', intro=intro,
        form=form, item=instance, return_url=reverse('vitrine_admin:section_list', args=[section]),
        questions=instance.questions.all() if section == 'offres' and instance else None,
    ))


@editor_required
def question_edit(request, offer_pk, pk=None):
    offer = get_object_or_404(OffreEmploi, pk=offer_pk)
    instance = get_object_or_404(OffreQuestion, pk=pk, offre=offer) if pk else None
    form = OffreQuestionForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        question = form.save(commit=False)
        question.offre = offer
        question.save()
        messages.success(request, 'La question du formulaire a été enregistrée.')
        return redirect('vitrine_admin:section_edit', section='offres', pk=offer.pk)
    return render(request, 'vitrine/backoffice/form.html', _layout(
        title='Question de candidature', intro=f'Offre : {offer.titre}', form=form,
        return_url=reverse('vitrine_admin:section_edit', args=['offres', offer.pk]),
    ))


@editor_required
def messages_list(request):
    return render(request, 'vitrine/backoffice/inbox.html', _layout(
        title='Messages reçus', kind='messages', items=ContactMessage.objects.all(),
    ))


@editor_required
def message_detail(request, pk):
    item = get_object_or_404(ContactMessage, pk=pk)
    reply_form = ContactReplyForm(request.POST or None)
    if request.method == 'POST' and request.POST.get('action') == 'toggle':
        item.traite = not item.traite
        item.save(update_fields=['traite'])
        return redirect('vitrine_admin:message_detail', pk=pk)
    if request.method == 'POST' and request.POST.get('action') == 'reply' and reply_form.is_valid():
        try:
            send_contact_reply(item, reply_form.cleaned_data['message'])
        except MailNotConfigured:
            messages.error(request, 'L’envoi par e-mail n’est pas encore configuré. La réponse n’a pas été envoyée.')
        except MailDeliveryError:
            messages.error(request, 'L’envoi a échoué. Vérifiez la configuration et réessayez.')
        else:
            ContactReply.objects.create(contact=item, message=reply_form.cleaned_data['message'])
            item.traite = True
            item.save(update_fields=['traite'])
            messages.success(request, 'La réponse a été envoyée par e-mail.')
            return redirect('vitrine_admin:message_detail', pk=pk)
    return render(request, 'vitrine/backoffice/inbox_detail.html', _layout(
        title='Message de contact', kind='messages', item=item,
        reply_form=reply_form, reply_enabled=mail_ready(), replies=item.reponses.all(),
    ))


@editor_required
def applications_list(request):
    return render(request, 'vitrine/backoffice/inbox.html', _layout(
        title='Candidatures reçues', kind='applications',
        items=Candidature.objects.select_related('offre').all(),
    ))


@editor_required
def application_detail(request, pk):
    item = get_object_or_404(Candidature.objects.select_related('offre'), pk=pk)
    return render(request, 'vitrine/backoffice/inbox_detail.html', _layout(
        title='Candidature', kind='applications', item=item,
    ))


@editor_required
def application_cv(request, pk):
    item = get_object_or_404(Candidature, pk=pk)
    if not item.cv:
        raise Http404
    return FileResponse(item.cv.open('rb'), as_attachment=True, filename=f'CV-candidature-{item.pk}.pdf', content_type='application/pdf')
