from django.db import migrations, models


ANCIENNE_MISSION = (
    'Mettre des équipes formées et supervisées au service des opérations de '
    'manutention, avec rigueur, discipline et sécurité.'
)
NOUVELLE_MISSION = 'Rigueur, discipline et sécurité au quotidien.'
ANCIENNE_ACTIVITE = 'Caristes & chariots élévateurs'
NOUVELLE_ACTIVITE = 'Manutention mécanisée'
ANCIENNE_DESCRIPTION = (
    'Des caristes formés pour le chargement et le déchargement par chariots élévateurs.'
)
NOUVELLE_DESCRIPTION = (
    'Chargement, déchargement et déplacements de marchandises selon les exigences de chaque site.'
)


def actualiser_accueil(apps, schema_editor):
    db = schema_editor.connection.alias
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    Activite = apps.get_model('vitrine_app', 'Activite')
    sites = SiteContent.objects.using(db)
    sites.update(
        page_about_visible=False,
        page_activities_visible=False,
        page_partners_visible=False,
        page_events_visible=True,
        page_careers_visible=False,
        page_contact_visible=True,
    )
    sites.filter(metric_caristes__in=['200+', '200']).update(metric_caristes='+200')
    sites.filter(metric_casiers='300 000').update(metric_casiers='≈ 300 000')
    sites.filter(mission=ANCIENNE_MISSION).update(mission=NOUVELLE_MISSION)

    activities = Activite.objects.using(db)
    activities.filter(titre=ANCIENNE_ACTIVITE).update(titre=NOUVELLE_ACTIVITE)
    activities.filter(titre=NOUVELLE_ACTIVITE, description_courte=ANCIENNE_DESCRIPTION).update(
        description_courte=NOUVELLE_DESCRIPTION,
    )


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0023_presentation_concise')]

    operations = [
        migrations.AlterField(
            model_name='sitecontent', name='page_about_visible',
            field=models.BooleanField(default=False, verbose_name='Qui sommes-nous'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='page_activities_visible',
            field=models.BooleanField(default=False, verbose_name='Activités'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='page_partners_visible',
            field=models.BooleanField(default=False, verbose_name='Partenaires'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='page_careers_visible',
            field=models.BooleanField(default=False, verbose_name='Carrières et offres d’emploi'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='metric_caristes',
            field=models.CharField(default='+200', max_length=30, verbose_name='Caristes formés · chiffre'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='metric_casiers',
            field=models.CharField(default='≈ 300 000', max_length=30, verbose_name='Manipulations par jour · chiffre'),
        ),
        migrations.RunPython(actualiser_accueil, migrations.RunPython.noop),
    ]
