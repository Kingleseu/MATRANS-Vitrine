from django.db import migrations, models


ANCIEN_TEXTE = (
    'Permettre aux entreprises de se concentrer sur leur métier pendant que leurs '
    'opérations de manutention sont organisées, encadrées et suivies sur le terrain.'
)
NOUVEAU_TEXTE = (
    "Notre modèle d'externalisation sur mesure vous libère des contraintes RH liées "
    'à cette catégorie tout en veillant à la performance opérationnelle, vous permettant '
    'ainsi de sécuriser vos flux et de vous concentrer sur vos priorités stratégiques '
    'dans un esprit de partenariat durable.'
)


def actualiser_texte_par_defaut(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    SiteContent.objects.using(schema_editor.connection.alias).filter(
        raison_etre=ANCIEN_TEXTE,
    ).update(raison_etre=NOUVEAU_TEXTE)


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0019_sites_partenaires_activites')]

    operations = [
        migrations.AlterField(
            model_name='sitecontent',
            name='raison_etre',
            field=models.TextField(default=NOUVEAU_TEXTE, verbose_name='Raison d’être'),
        ),
        migrations.RunPython(actualiser_texte_par_defaut, migrations.RunPython.noop),
    ]
