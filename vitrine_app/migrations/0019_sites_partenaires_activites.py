from django.db import migrations, models


MANUELS = ('cd-bandundu', 'cd-tshikapa', 'cd-kananga')
MECANISES = (
    'cd-bumbu', 'cd-franco', 'cd-gombe', 'cd-kimbanseke', 'cd-maluku',
    'cd-matadi', 'cd-mbandaka', 'cd-mbanza-ngungu', 'cd-mbudi',
    'cd-triangle', 'cd-meferco', 'cd-boma',
)


def actualiser_sites(apps, schema_editor):
    db = schema_editor.connection.alias
    Site = apps.get_model('vitrine_app', 'CentreVitrine')
    sites = Site.objects.using(db)

    sites.filter(code__in=MANUELS).update(categorie_activite='manuelle')
    sites.filter(code='cd-kikwit').update(categorie_activite='mixte')
    sites.filter(code__in=MECANISES, categorie_activite='').update(
        categorie_activite='mecanisee',
    )

    sites.filter(code='cd-franco', nom='CD FRANCKO').update(nom='CD FRANCO')
    sites.filter(code='cd-franco', ville='Ville à confirmer').update(ville='Kinshasa')
    sites.filter(code='cd-franco', province='').update(province='Kinshasa')
    sites.filter(code='cd-triangle', ville='Ville à confirmer').update(ville='Kinshasa')
    sites.filter(code='cd-triangle', province='').update(province='Kinshasa')
    sites.filter(code='cd-bandundu', nom='CD BANDUNDU').update(nom='Bandundu-Ville')
    sites.filter(code='cd-bandundu', ville='Bandundu').update(ville='Bandundu-Ville')
    sites.filter(code='cd-bandundu', zone_carte='Bandundu').update(zone_carte='Bandundu-Ville')
    sites.filter(code='cd-tshikapa', nom='CD TSHIKAPA').update(nom='Tshikapa')
    sites.filter(code='cd-kananga', nom='CD KANANGA').update(nom='Kananga')

    for code, name, alternatives, city, province, zone, latitude, longitude, order in (
        ('site-mid-usine', 'MID/Usine', ('MID/Usine', 'MID / Usine'),
         'Kinshasa', 'Kinshasa', 'Kinshasa', '-4.320000', '15.300000', 17),
        ('site-muanda', 'Muanda', ('Muanda', 'CD MUANDA'),
         'Muanda', 'Kongo Central', 'Muanda', '-5.927525', '12.371476', 18),
    ):
        site = sites.filter(code=code).first()
        if site is None:
            site = sites.filter(nom__in=alternatives).first()
        if site is None:
            sites.create(
                code=code, nom=name, ville=city, province=province,
                zone_carte=zone, latitude=latitude, longitude=longitude,
                categorie_activite='mecanisee', localisation_indicative=True,
                publie=True, ordre=order,
            )
        elif not site.categorie_activite:
            sites.filter(pk=site.pk).update(categorie_activite='mecanisee')


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0018_texte_banniere_matrans')]

    operations = [
        migrations.AddField(
            model_name='centrevitrine', name='categorie_activite',
            field=models.CharField(
                blank=True,
                choices=[
                    ('mecanisee', 'Manutention mécanisée'),
                    ('manuelle', 'Manutention manuelle'),
                    ('mixte', 'Mixte'),
                ],
                default='', max_length=10, verbose_name="Catégorie d'activité",
            ),
        ),
        migrations.AlterField(
            model_name='centrevitrine', name='nom',
            field=models.CharField(max_length=130, verbose_name='Nom du site'),
        ),
        migrations.AlterField(
            model_name='centrevitrine', name='zone_carte',
            field=models.CharField(
                blank=True, max_length=120,
                help_text='Les sites ayant le même nom de zone partagent un repère sur la carte. Celui-ci est placé au centre de leurs positions indicatives.',
                verbose_name='Point regroupé sur la carte',
            ),
        ),
        migrations.AlterModelOptions(
            name='centrevitrine',
            options={
                'ordering': ['ordre', 'nom'],
                'verbose_name': 'Site partenaire public',
                'verbose_name_plural': 'Sites partenaires publics',
            },
        ),
        migrations.RunPython(actualiser_sites, migrations.RunPython.noop),
    ]
