from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from .storage import PrivateApplicationStorage


class SiteContent(models.Model):
    """Contenu éditorial et coordonnées de la vitrine (une seule fiche)."""

    hero_kicker = models.CharField(max_length=100, default='MATRANS S.A.R.L. · République démocratique du Congo')
    hero_title = models.CharField(max_length=180, default='Vous gérez votre métier.')
    hero_title_accent = models.CharField('Suite du titre en orange', max_length=180, blank=True, default='')
    hero_text = models.TextField(default='Spécialiste de la manutention, MATRANS S.A.R.L. s’appuie sur des équipes expérimentées et un encadrement rigoureux pour accompagner vos opérations, avec une ouverture vers le transport de marchandises.')
    hero_image = models.ImageField("Image d'accueil", upload_to='vitrine/accueil/', blank=True, help_text="Remplace l'illustration provisoire de l'accueil.")
    about_title = models.CharField(max_length=160, default='Des équipes engagées au cœur de vos flux.')
    about_intro = models.TextField(default='MATRANS S.A.R.L. organise le chargement et le déchargement par chariots élévateurs, encadre les équipes sur site et accompagne les opérations de distribution en RDC.')
    about_body = models.TextField(blank=True)
    about_distribution_image = models.ImageField('Image de distribution', upload_to='vitrine/presentation/', blank=True, help_text="Remplace l'illustration de distribution sur l'accueil et la présentation.")
    about_handling_image = models.ImageField('Image de manutention', upload_to='vitrine/presentation/', blank=True, help_text="Remplace l'illustration de manutention sur l'accueil et la présentation.")
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    raison_etre = models.TextField('Raison d’être', default='Permettre aux entreprises de se concentrer sur leur métier pendant que leurs opérations de manutention sont organisées, encadrées et suivies sur le terrain.')
    objectifs = models.TextField('Nos objectifs', default='Assurer la continuité des opérations, adapter les équipes aux volumes de chaque site et améliorer la sécurité, la qualité et la cadence grâce au suivi de terrain.')
    plus_value = models.TextField('Notre plus-value', default='Un dispositif qui recrute et forme, affecte les équipes, supervise les opérations, organise les remplacements et suit les incidents comme la cadence.')
    historique = models.TextField('Notre parcours', default='La présentation commerciale de MATRANS retrace une collaboration avec BRACONGO commencée à l’usine centrale, puis étendue aux centres de distribution de Kinshasa et de province. Ce parcours illustre le développement de son organisation de terrain.')
    valeurs = models.TextField('Nos valeurs', default='Rigueur dans l’organisation, discipline au quotidien et sécurité sur chaque site : ces principes guident l’encadrement des équipes.')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_address = models.CharField(max_length=255, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    show_team = models.BooleanField(default=False, verbose_name="Afficher l'équipe")
    metric_caristes = models.CharField('Caristes formés · chiffre', max_length=30, default='200+')
    metric_manutentionnaires = models.CharField('Manutentionnaires gérés · chiffre', max_length=30, default='100+')
    metric_casiers = models.CharField('Manipulations par jour · chiffre', max_length=30, default='300 000')
    metric_incidents = models.CharField('Évolution des incidents chez BRACONGO · chiffre', max_length=30, default='-30 %')
    metric_source = models.CharField('Source et période des chiffres', max_length=220, default='Présentation commerciale MATRANS 2026 ; volume quotidien confirmé par MATRANS le 30 octobre 2026')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contenu du site'

    def __str__(self):
        return 'Contenu du site vitrine'

class Activite(models.Model):
    titre = models.CharField("Titre de l'activité", max_length=150)
    icone = models.CharField("Classe Icône FontAwesome", max_length=50, blank=True, help_text="Ex: fa-truck, fa-boxes, fa-ship")
    description_courte = models.TextField("Résumé (Page d'accueil)", max_length=300)
    description_complete = models.TextField("Description détaillée")
    image = models.ImageField("Image d'illustration", upload_to="activites/", blank=True)
    ordre = models.IntegerField("Ordre d'affichage", default=0)
    publiee = models.BooleanField('Visible sur le site', default=True)

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ['ordre']

    def __str__(self):
        return self.titre


class CentreVitrine(models.Model):
    """Fiche publique indépendante des données opérationnelles des CD."""

    code = models.SlugField('Identifiant', max_length=80, unique=True)
    nom = models.CharField('Nom du centre', max_length=130)
    ville = models.CharField('Ville / commune', max_length=120, blank=True)
    province = models.CharField('Province', max_length=120, blank=True)
    zone_carte = models.CharField(
        'Point regroupé sur la carte', max_length=120, blank=True,
        help_text='Les centres ayant le même nom de zone partagent un repère sur la carte. Celui-ci est placé au centre de leurs positions indicatives.',
    )
    description = models.TextField('Présentation publique', blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text='Latitude décimale. Une position approximative peut être corrigée ici.',
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text='Longitude décimale. Utilisez le même point pour les centres d’une zone regroupée.',
    )
    localisation_indicative = models.BooleanField(
        'Position indicative', default=True,
        help_text='Laissez cette option active tant que la localisation exacte du centre n’est pas confirmée.',
    )
    publie = models.BooleanField('Visible sur le site', default=False)
    ordre = models.PositiveIntegerField('Ordre d’affichage', default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Centre de distribution public'
        verbose_name_plural = 'Centres de distribution publics'

    def __str__(self):
        return self.nom


class Partenaire(models.Model):
    nom = models.CharField("Nom de l'entreprise / Client", max_length=150)
    logo = models.ImageField("Logo de l'entreprise", upload_to="partenaires/", blank=True)
    site_web = models.URLField("Lien vers leur site", blank=True, null=True)
    description = models.CharField("Secteur ou type de collaboration", max_length=200, blank=True)
    ordre = models.IntegerField("Ordre d'affichage", default=0)
    publie = models.BooleanField('Visible sur le site', default=False)

    class Meta:
        verbose_name = "Partenaire / Client"
        verbose_name_plural = "Partenaires & Clients"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class OffreEmploi(models.Model):
    TYPE_CONTRAT = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('STAGE', 'Stage'),
        ('PRESTATION', 'Prestation / Consultant'),
    ]

    titre = models.CharField("Titre du poste", max_length=150)
    lieu = models.CharField("Lieu de travail", max_length=100, default="Kinshasa")
    type_contrat = models.CharField("Type de contrat", max_length=20, choices=TYPE_CONTRAT, default='CDI')
    description = models.TextField("Missions & Responsabilités")
    profil_recherche = models.TextField("Compétences & Qualifications requises")
    est_active = models.BooleanField("Offre ouverte", default=True)
    date_limite = models.DateField("Date limite de candidature", null=True, blank=True)
    date_publication = models.DateTimeField("Date de publication", auto_now_add=True)

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.titre} ({self.type_contrat}) - {self.lieu}"

    @property
    def ouverte(self):
        return self.est_active and (not self.date_limite or self.date_limite >= timezone.localdate())


class OffreQuestion(models.Model):
    TYPES = [('text', 'Réponse courte'), ('textarea', 'Réponse longue'), ('select', 'Choix unique')]
    offre = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, related_name='questions')
    libelle = models.CharField(max_length=180)
    type_champ = models.CharField(max_length=12, choices=TYPES, default='text')
    choix = models.TextField(blank=True, help_text='Pour un choix unique : une option par ligne.')
    obligatoire = models.BooleanField(default=False)
    actif = models.BooleanField('Afficher cette question', default=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'pk']

    def __str__(self):
        return self.libelle


class Evenement(models.Model):
    titre = models.CharField(max_length=180)
    resume = models.CharField(max_length=320)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField(null=True, blank=True)
    lieu = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to='vitrine/evenements/', blank=True)
    publie = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'

    def __str__(self):
        return self.titre


class MembreEquipe(models.Model):
    nom = models.CharField(max_length=130)
    fonction = models.CharField(max_length=150)
    presentation = models.TextField(blank=True)
    photo = models.ImageField(upload_to='vitrine/equipe/', blank=True)
    ordre = models.PositiveIntegerField(default=0)
    publie = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"

    def __str__(self):
        return self.nom


class Candidature(models.Model):
    offre = models.ForeignKey(OffreEmploi, on_delete=models.SET_NULL, related_name='candidatures', null=True, blank=True)
    nom_complet = models.CharField("Nom et Prénom", max_length=150)
    email = models.EmailField("Adresse Email")
    telephone = models.CharField("Numéro de Téléphone", max_length=20)
    cv = models.FileField("Document CV (PDF)", upload_to="cvs/", storage=PrivateApplicationStorage())
    lettre_motivation = models.TextField("Lettre de motivation ou Message", blank=True)
    reponses = models.JSONField(default=dict, blank=True)
    consentement = models.BooleanField(default=False)
    domaine = models.CharField(max_length=120, blank=True)
    date_postulation = models.DateTimeField("Date de postulation", auto_now_add=True)

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures reçues"
        ordering = ['-date_postulation']

    def __str__(self):
        return f"{self.nom_complet} - {self.offre.titre if self.offre else 'Candidature spontanée'}"


class ContactMessage(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    telephone = models.CharField(max_length=50, blank=True)
    sujet = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    notification_status = models.CharField(
        'Notification e-mail', max_length=20,
        choices=[('non_configure', 'Non configurée'), ('envoye', 'Envoyée'), ('erreur', 'Échec')],
        default='non_configure',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f'{self.nom} — {self.sujet}'


class ContactReply(models.Model):
    contact = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='reponses')
    message = models.TextField('Réponse envoyée')
    sent_at = models.DateTimeField('Envoyée le', auto_now_add=True)

    class Meta:
        ordering = ['sent_at']
        verbose_name = 'Réponse à un contact'
        verbose_name_plural = 'Réponses aux contacts'

    def __str__(self):
        return f'Réponse à {self.contact.nom}'
