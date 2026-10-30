from django.db import migrations
from django.utils.text import slugify


def villes_en_centres(apps, schema_editor):
    db = schema_editor.connection.alias
    PresenceVille = apps.get_model('vitrine_app', 'PresenceVille')
    CentreVitrine = apps.get_model('vitrine_app', 'CentreVitrine')

    for ville in PresenceVille.objects.using(db).all():
        CentreVitrine.objects.using(db).get_or_create(
            code=f'cd-{slugify(ville.ville)}',
            defaults={
                'nom': f'CD {ville.ville.upper()}',
                'ville': ville.ville,
                'province': ville.province,
                'zone_carte': ville.ville,
                'latitude': ville.latitude,
                'longitude': ville.longitude,
                'localisation_indicative': True,
                'publie': ville.publie,
                'ordre': 100 + ville.ordre,
            },
        )


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0014_presence_and_company_updates')]

    operations = [
        migrations.RunPython(villes_en_centres, migrations.RunPython.noop),
        migrations.DeleteModel(name='PresenceVille'),
    ]
