from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Activite, Candidature, CentreVitrine, ContactMessage, ContactReply, Evenement, MembreEquipe,
    OffreEmploi, OffreQuestion, Partenaire, SiteContent,
)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            widget.attrs['class'] = 'form-check-input' if isinstance(widget, forms.CheckboxInput) else 'form-control'


class SiteContentForm(StyledModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields([
            'hero_kicker', 'hero_title', 'hero_title_accent', 'hero_text', 'hero_image',
            'metric_caristes', 'metric_manutentionnaires', 'metric_casiers',
            'metric_incidents', 'metric_source',
            'about_title', 'about_intro', 'about_body',
            'about_distribution_image', 'about_handling_image',
            'raison_etre', 'mission', 'objectifs', 'plus_value', 'historique', 'valeurs', 'vision',
            'contact_email', 'contact_phone',
            'contact_address', 'facebook_url', 'instagram_url',
            'linkedin_url', 'youtube_url', 'show_team',
        ])
        self.fields['metric_source'].help_text = 'Indiquez la date et la provenance des chiffres affichés sur l’accueil.'

    class Meta:
        model = SiteContent
        exclude = ['updated_at']
        widgets = {
            'hero_text': forms.Textarea(attrs={'rows': 3}),
            'about_intro': forms.Textarea(attrs={'rows': 3}),
            'about_body': forms.Textarea(attrs={'rows': 5}),
            'mission': forms.Textarea(attrs={'rows': 3}),
            'raison_etre': forms.Textarea(attrs={'rows': 3}),
            'objectifs': forms.Textarea(attrs={'rows': 3}),
            'plus_value': forms.Textarea(attrs={'rows': 3}),
            'historique': forms.Textarea(attrs={'rows': 4}),
            'valeurs': forms.Textarea(attrs={'rows': 3}),
            'vision': forms.Textarea(attrs={'rows': 3}),
        }


class ActiviteForm(StyledModelForm):
    class Meta:
        model = Activite
        exclude = []


class CentreVitrineForm(StyledModelForm):
    class Meta:
        model = CentreVitrine
        fields = [
            'code', 'nom', 'ville', 'province', 'categorie_activite', 'zone_carte', 'description',
            'latitude', 'longitude', 'localisation_indicative', 'publie', 'ordre',
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def clean(self):
        data = super().clean()
        if data.get('publie') and not data.get('categorie_activite'):
            raise ValidationError("Choisissez le type d'activité avant de publier ce site.")
        if (data.get('latitude') is None) != (data.get('longitude') is None):
            raise ValidationError('Renseignez la latitude et la longitude ensemble.')
        latitude, longitude = data.get('latitude'), data.get('longitude')
        if latitude is not None and longitude is not None and not (
            Decimal('-13.5') <= latitude <= Decimal('5.4')
            and Decimal('12.2') <= longitude <= Decimal('31.3')
        ):
            raise ValidationError('Le point doit se trouver en République démocratique du Congo.')
        return data


class PartenaireForm(StyledModelForm):
    class Meta:
        model = Partenaire
        exclude = []


class OffreEmploiForm(StyledModelForm):
    class Meta:
        model = OffreEmploi
        exclude = ['date_publication']
        widgets = {'date_limite': forms.DateInput(attrs={'type': 'date'})}


class OffreQuestionForm(StyledModelForm):
    class Meta:
        model = OffreQuestion
        fields = ['libelle', 'type_champ', 'choix', 'obligatoire', 'actif', 'ordre']

    def clean(self):
        data = super().clean()
        if data.get('type_champ') == 'select' and not (data.get('choix') or '').strip():
            self.add_error('choix', 'Indiquez au moins une option pour ce champ.')
        return data


class EvenementForm(StyledModelForm):
    class Meta:
        model = Evenement
        exclude = ['created_at']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class MembreEquipeForm(StyledModelForm):
    class Meta:
        model = MembreEquipe
        exclude = []


class ContactForm(StyledModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'telephone', 'sujet', 'message']

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise ValidationError('Message non accepté.')
        return ''


class ContactReplyForm(StyledModelForm):
    class Meta:
        model = ContactReply
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Rédigez votre réponse…'})}


class CandidatureForm(StyledModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    consentement = forms.BooleanField(
        label="J'accepte que MATRANS utilise les informations transmises pour étudier ma candidature.",
        required=True,
    )

    class Meta:
        model = Candidature
        fields = ['nom_complet', 'email', 'telephone', 'cv', 'lettre_motivation', 'consentement']
        widgets = {'cv': forms.FileInput(attrs={'accept': '.pdf,application/pdf'})}

    def __init__(self, *args, offre=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.offre = offre
        if offre:
            for question in offre.questions.filter(actif=True):
                name = f'question_{question.pk}'
                options = [line.strip() for line in question.choix.splitlines() if line.strip()]
                if question.type_champ == 'select':
                    field = forms.ChoiceField(choices=[('', 'Choisir…')] + [(x, x) for x in options])
                elif question.type_champ == 'textarea':
                    field = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
                else:
                    field = forms.CharField(max_length=500)
                field.label = question.libelle
                field.required = question.obligatoire
                field.widget.attrs['class'] = 'form-control'
                self.fields[name] = field

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise ValidationError('Candidature non acceptée.')
        return ''

    def clean_cv(self):
        cv = self.cleaned_data['cv']
        if cv.size > 5 * 1024 * 1024:
            raise ValidationError('Le CV doit peser moins de 5 Mo.')
        if not cv.name.lower().endswith('.pdf') or cv.read(5) != b'%PDF-':
            raise ValidationError('Envoyez un fichier PDF valide.')
        cv.seek(0)
        return cv

    def save(self, commit=True):
        application = super().save(commit=False)
        application.offre = self.offre
        if self.offre:
            application.reponses = {
                str(question.pk): {'question': question.libelle, 'reponse': self.cleaned_data.get(f'question_{question.pk}', '')}
                for question in self.offre.questions.filter(actif=True)
            }
        if commit:
            application.save()
        return application
