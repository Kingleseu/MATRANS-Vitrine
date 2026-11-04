from django.db import migrations, models


NOUVELLE_BANNIERE = (
    'Matrans SARL est une entreprise spécialisée dans les opérations de manutention, '
    'avec une extension naturelle vers le transport.'
)
ANCIENNE_BANNIERE = (
    'Matrans SARL est spécialisée dans la manutention et étend ses activités au transport. '
    'Nous encadrons et suivons vos opérations pour renforcer la sécurité, réduire les incidents '
    'et assurer la régularité des équipes de caristes et de manutentionnaires.'
)
NOUVELLE_MISSION = (
    'Nous mettons à votre disposition un encadrement et un suivi opérationnel rigoureux '
    'pour répondre aux défis majeurs de votre Supply Chain : sécurité, réduction des '
    'incidents et régularité des effectifs (caristes ou manutentionnaires).'
)


def actualiser_textes(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    contenus = SiteContent.objects.using(schema_editor.connection.alias)
    contenus.filter(hero_text=ANCIENNE_BANNIERE).update(hero_text=NOUVELLE_BANNIERE)
    contenus.filter(mission__in=['', 'Rigueur, discipline et sécurité au quotidien.']).update(
        mission=NOUVELLE_MISSION,
    )


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0024_accueil_trois_pages')]

    operations = [
        migrations.AlterField(
            model_name='sitecontent', name='hero_text',
            field=models.TextField(default=NOUVELLE_BANNIERE),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='mission',
            field=models.TextField(blank=True, default=NOUVELLE_MISSION),
        ),
        migrations.RunPython(actualiser_textes, migrations.RunPython.noop),
    ]
