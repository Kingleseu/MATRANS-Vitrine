from django.db import migrations


CENTRES = [
    ('cd-bumbu', 'CD BUMBU', 'Bumbu', 'Kinshasa', 'Kinshasa', -4.320000, 15.300000),
    ('cd-franco', 'CD FRANCO', 'Ville à confirmer', '', 'Kinshasa', -4.320000, 15.300000),
    ('cd-gombe', 'CD GOMBE', 'Gombe', 'Kinshasa', 'Kinshasa', -4.320000, 15.300000),
    ('cd-kikwit', 'CD KIKWIT', 'Kikwit', 'Kwilu', 'Kikwit', -5.039400, 18.784000),
    ('cd-kimbanseke', 'CD KIMBANSEKE', 'Kimbanseke', 'Kinshasa', 'Kinshasa', -4.320000, 15.300000),
    ('cd-maluku', 'CD MALUKU', 'Maluku', 'Kinshasa', 'Kinshasa', -4.320000, 15.300000),
    ('cd-matadi', 'CD MATADI', 'Matadi', 'Kongo Central', 'Matadi', -5.794500, 13.440300),
    ('cd-mbandaka', 'CD MBANDAKA', 'Mbandaka', 'Équateur', 'Mbandaka', 0.021400, 18.291100),
    ('cd-mbanza-ngungu', 'CD MBANZA NGUNGU', 'Mbanza-Ngungu', 'Kongo Central', 'Mbanza-Ngungu', -5.200000, 14.850000),
    ('cd-mbudi', 'CD MBUDI', 'Mbudi', 'Kinshasa', 'Kinshasa', -4.320000, 15.300000),
    ('cd-triangle', 'CD TRIANGLE', 'Ville à confirmer', '', 'Kinshasa', -4.320000, 15.300000),
]


def create_centres(apps, schema_editor):
    CentreVitrine = apps.get_model('vitrine_app', 'CentreVitrine')
    db = schema_editor.connection.alias
    for order, (code, nom, ville, province, zone, latitude, longitude) in enumerate(CENTRES, start=1):
        CentreVitrine.objects.using(db).get_or_create(code=code, defaults={
            'nom': nom,
            'ville': ville,
            'province': province,
            'zone_carte': zone,
            'latitude': latitude,
            'longitude': longitude,
            'localisation_indicative': True,
            'publie': True,
            'ordre': order,
        })


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0005_centrevitrine')]
    operations = [migrations.RunPython(create_centres, migrations.RunPython.noop)]
