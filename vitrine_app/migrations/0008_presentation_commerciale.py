from django.db import migrations


def enrich_vitrine(apps, schema_editor):
    db = schema_editor.connection.alias
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    Activite = apps.get_model('vitrine_app', 'Activite')
    Partenaire = apps.get_model('vitrine_app', 'Partenaire')

    site, created = SiteContent.objects.using(db).get_or_create(pk=1)
    changes = {}
    old_defaults = {
        'hero_kicker': 'Distribution & manutention',
        'hero_title': 'Chaque mouvement compte.',
        'hero_text': 'MATRANS accompagne les opérations de distribution et de manutention, du centre de distribution jusqu’au terrain.',
        'about_title': 'Au cœur de la distribution.',
        'about_intro': 'La distribution et la manutention prennent forme grâce aux équipes, à l’organisation des flux et à l’attention portée à chaque opération.',
    }
    new_copy = {
        'hero_kicker': 'MATRANS S.A.R.L. · République démocratique du Congo',
        'hero_title': 'Vous gérez votre métier. Nous gérons votre manutention.',
        'hero_text': 'Chargement, déchargement et encadrement des caristes et manutentionnaires : des équipes supervisées pour faire avancer vos opérations.',
        'about_title': 'Des équipes engagées au cœur de vos flux.',
        'about_intro': 'MATRANS S.A.R.L. organise le chargement et le déchargement par chariots élévateurs, encadre les équipes sur site et accompagne les opérations de distribution en RDC.',
    }
    for field, value in new_copy.items():
        if created or getattr(site, field) == old_defaults[field]:
            changes[field] = value
    if not site.about_body:
        changes['about_body'] = (
            'Notre métier est de recruter, former et encadrer les caristes et les manutentionnaires au quotidien. '
            'Nos superviseurs planifient les équipes, suivent les présences, la cadence et les incidents, puis organisent les actions correctives nécessaires.\n\n'
            'Cette méthode accompagne le chargement et le déchargement en usine, en centre de distribution, sur quai et sur d’autres plateformes logistiques.'
        )
    if not site.mission:
        changes['mission'] = 'Mettre des équipes formées et supervisées au service des opérations de manutention, avec rigueur, discipline et sécurité.'
    if not site.vision:
        changes['vision'] = 'Développer une organisation de terrain fiable, capable de suivre les opérations et de s’adapter aux besoins de chaque site.'
    if not site.contact_email:
        changes['contact_email'] = 'contact@matrans-rdc.com'
    if not site.contact_phone:
        changes['contact_phone'] = '+243 98 21 86 167'
    if not site.contact_address:
        changes['contact_address'] = '04, Avenue de la Justice, Kinshasa / Gombe'
    if changes:
        SiteContent.objects.using(db).filter(pk=site.pk).update(**changes)

    if not Activite.objects.using(db).exists():
        activities = [
            ('Chargement & déchargement', 'Des caristes et manutentionnaires formés pour les opérations de chargement et de déchargement.', 'Nous organisons les équipes et les moyens de manutention selon les volumes, les horaires et les contraintes du site.', 1),
            ('Encadrement des équipes', 'Une supervision présente sur le terrain pour coordonner les agents, les remplacements et la sécurité.', 'Les superviseurs accompagnent les caristes et manutentionnaires, suivent les présences et assurent la continuité des équipes.', 2),
            ('Distribution & plateformes', 'Des opérations suivies en usine, en centre de distribution et sur les plateformes logistiques.', 'Notre expérience couvre les centres de distribution, les quais et les espaces de chargement. Les sites publics présentés sur la carte restent à confirmer individuellement.', 3),
            ('Suivi opérationnel', 'Présence, cadence, incidents et casse : des informations suivies pour agir rapidement.', 'Nous planifions, affectons, supervisons et mesurons les opérations afin d’identifier les points à corriger.', 4),
        ]
        for title, short, detail, order in activities:
            Activite.objects.using(db).create(titre=title, description_courte=short, description_complete=detail, ordre=order, publiee=True)

    Partenaire.objects.using(db).get_or_create(nom='BRACONGO', defaults={
        'description': 'Collaboration présentée dans le profil commercial MATRANS (2026).',
        'ordre': 1,
        'publie': True,
    })


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0007_sitecontent_metric_caristes_and_more')]
    operations = [migrations.RunPython(enrich_vitrine, migrations.RunPython.noop)]
