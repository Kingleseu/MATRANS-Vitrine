from django.db import migrations


def apply_corrections(apps, schema_editor):
    db = schema_editor.connection.alias
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    CentreVitrine = apps.get_model('vitrine_app', 'CentreVitrine')
    Activite = apps.get_model('vitrine_app', 'Activite')

    full_title = 'Vous gérez votre métier. Nous gérons votre manutention.'
    SiteContent.objects.using(db).filter(hero_title=full_title, hero_title_accent='').update(
        hero_title='Vous gérez votre métier.',
        hero_title_accent='Nous gérons votre manutention.',
    )
    SiteContent.objects.using(db).filter(metric_casiers='250 000').update(metric_casiers='3 000 000')
    SiteContent.objects.using(db).filter(
        metric_source='Présentation commerciale MATRANS, octobre 2026 · chiffres communiqués par l’entreprise'
    ).update(
        metric_source='Présentation commerciale 2026 et correction du volume quotidien communiquée par MATRANS le 30 octobre 2026'
    )

    CentreVitrine.objects.using(db).filter(code='cd-franco', nom='CD FRANCO').update(nom='CD FRANCKO')
    CentreVitrine.objects.using(db).filter(code='cd-matadi', zone_carte='Matadi').update(zone_carte='Kongo Central')
    CentreVitrine.objects.using(db).filter(code='cd-mbanza-ngungu', zone_carte='Mbanza-Ngungu').update(zone_carte='Kongo Central')
    CentreVitrine.objects.using(db).get_or_create(code='cd-limete', defaults={
        'nom': 'CD LIMETE', 'ville': 'Limete', 'province': 'Kinshasa',
        'zone_carte': 'Kinshasa', 'latitude': -4.320000, 'longitude': 15.300000,
        'localisation_indicative': True, 'publie': True, 'ordre': 12,
    })
    CentreVitrine.objects.using(db).get_or_create(code='cd-boma', defaults={
        'nom': 'CD BOMA', 'ville': 'Boma', 'province': 'Kongo Central',
        'zone_carte': 'Kongo Central', 'latitude': -5.850980, 'longitude': 13.053640,
        'localisation_indicative': True, 'publie': True, 'ordre': 13,
    })

    seeded = [
        (
            'Chargement & déchargement',
            'Des caristes et manutentionnaires formés pour les opérations de chargement et de déchargement.',
            'Manutention manuelle',
            'Des équipes pour le chargement, le déchargement et le transbordement manuel des marchandises.',
            'MATRANS organise la manutention manuelle sur les sites de distribution et les plateformes logistiques. Les équipes sont affectées selon les volumes et les contraintes du terrain.',
        ),
        (
            'Encadrement des équipes',
            'Une supervision présente sur le terrain pour coordonner les agents, les remplacements et la sécurité.',
            'Caristes & chariots élévateurs',
            'Des caristes formés pour le chargement et le déchargement par chariots élévateurs.',
            'Les caristes interviennent sur les plateformes, dans les centres de distribution et aux points de chargement. La lettre commerciale décrit notamment leur déploiement en usine et au centre de Meferco.',
        ),
        (
            'Distribution & plateformes',
            'Des opérations suivies en usine, en centre de distribution et sur les plateformes logistiques.',
            'Supervision des équipes',
            'Des superviseurs présents sur site pour coordonner les shifts, les présences et les remplacements.',
            'Le modèle MATRANS comprend l’encadrement quotidien des caristes et manutentionnaires, le suivi des présences et l’organisation des remplacements pour assurer la continuité du service.',
        ),
        (
            'Suivi opérationnel',
            'Présence, cadence, incidents et casse : des informations suivies pour agir rapidement.',
            'Suivi, sécurité & continuité',
            'Incidents, casse, discipline et cadence sont suivis pour améliorer les opérations.',
            'La supervision relève les incidents, la casse, les présences et la cadence. Ces informations soutiennent les actions correctives, les rappels et la formation continue.',
        ),
    ]
    updated = 0
    for old_title, old_short, title, short, detail in seeded:
        updated += Activite.objects.using(db).filter(
            titre=old_title, description_courte=old_short,
        ).update(titre=title, description_courte=short, description_complete=detail)
    if updated:
        Activite.objects.using(db).get_or_create(titre='Centres & plateformes', defaults={
            'description_courte': 'Une présence dans les centres de distribution et sur différents sites de manutention.',
            'description_complete': 'L’expérience présentée par MATRANS couvre des centres à Kinshasa et en province. La carte publique montre les centres connus ; leur position exacte reste à confirmer dans le studio.',
            'ordre': 5, 'publiee': True,
        })


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0010_alter_sitecontent_metric_source')]
    operations = [migrations.RunPython(apply_corrections, migrations.RunPython.noop)]
