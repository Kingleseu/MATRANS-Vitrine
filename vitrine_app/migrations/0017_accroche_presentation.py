from django.db import migrations, models


ANCIEN_TEXTE = (
    'Spécialiste de la manutention, MATRANS S.A.R.L. s’appuie sur des équipes '
    'expérimentées et un encadrement rigoureux pour accompagner vos opérations, '
    'avec une ouverture vers le transport de marchandises.'
)
NOUVEAU_TEXTE = (
    'Nous formons et accompagnons les équipes de manutention au plus près du terrain. '
    'Une organisation rigoureuse, attentive à la sécurité, permet à vos opérations '
    'd’avancer avec confiance.'
)


def actualiser_accroche(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    SiteContent.objects.using(schema_editor.connection.alias).filter(
        hero_text=ANCIEN_TEXTE,
    ).update(hero_text=NOUVEAU_TEXTE)


class Migration(migrations.Migration):
    dependencies = [
        ('vitrine_app', '0016_identite_matrans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitecontent',
            name='hero_text',
            field=models.TextField(default=NOUVEAU_TEXTE),
        ),
        migrations.RunPython(actualiser_accroche, migrations.RunPython.noop),
    ]
