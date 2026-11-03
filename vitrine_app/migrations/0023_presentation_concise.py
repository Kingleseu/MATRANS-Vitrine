from django.db import migrations, models


ANCIENNE_BANNIERE = (
    'Matrans SARL est une entreprise spécialisée dans les opérations de manutention, '
    'avec une extension naturelle vers le transport. Nous mettons à votre disposition '
    'un encadrement et un suivi opérationnel rigoureux pour répondre aux défis majeurs '
    'de votre Supply Chain : sécurité, réduction des incidents et régularité des '
    'effectifs (caristes ou manutentionnaires).'
)
NOUVELLE_BANNIERE = (
    'Matrans SARL est spécialisée dans la manutention et étend ses activités au transport. '
    'Nous encadrons et suivons vos opérations pour renforcer la sécurité, réduire les incidents '
    'et assurer la régularité des équipes de caristes et de manutentionnaires.'
)
ANCIENNES_VALEURS = (
    'Rigueur dans l’organisation, discipline au quotidien et sécurité sur chaque site : '
    'ces principes guident l’encadrement des équipes.'
)
NOUVELLES_VALEURS = (
    'Ces principes guident l’organisation des équipes, les décisions sur le terrain '
    'et l’attention portée aux personnes comme aux marchandises.'
)


def actualiser_textes_par_defaut(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    contenus = SiteContent.objects.using(schema_editor.connection.alias)
    contenus.filter(hero_text=ANCIENNE_BANNIERE).update(hero_text=NOUVELLE_BANNIERE)
    contenus.filter(valeurs=ANCIENNES_VALEURS).update(valeurs=NOUVELLES_VALEURS)


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0022_visibilite_pages')]

    operations = [
        migrations.AlterField(
            model_name='sitecontent', name='hero_text',
            field=models.TextField(default=NOUVELLE_BANNIERE),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='valeurs',
            field=models.TextField(default=NOUVELLES_VALEURS, verbose_name='Nos valeurs'),
        ),
        migrations.RunPython(actualiser_textes_par_defaut, migrations.RunPython.noop),
    ]
