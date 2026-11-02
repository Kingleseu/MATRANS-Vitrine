from django.db import migrations, models


ANCIEN_TEXTE = (
    'Nous formons et accompagnons les équipes de manutention au plus près du terrain. '
    'Une organisation rigoureuse, attentive à la sécurité, permet à vos opérations '
    'd’avancer avec confiance.'
)
NOUVEAU_TEXTE = (
    'Matrans SARL est une entreprise spécialisée dans les opérations de manutention, '
    'avec une extension naturelle vers le transport. Nous mettons à votre disposition '
    'un encadrement et un suivi opérationnel rigoureux pour répondre aux défis majeurs '
    'de votre Supply Chain : sécurité, réduction des incidents et régularité des '
    'effectifs (caristes ou manutentionnaires).'
)


def actualiser_banniere(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    SiteContent.objects.using(schema_editor.connection.alias).filter(
        hero_text=ANCIEN_TEXTE,
    ).update(hero_text=NOUVEAU_TEXTE)


class Migration(migrations.Migration):
    dependencies = [
        ('vitrine_app', '0017_accroche_presentation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitecontent',
            name='hero_text',
            field=models.TextField(default=NOUVEAU_TEXTE),
        ),
        migrations.RunPython(actualiser_banniere, migrations.RunPython.noop),
    ]
