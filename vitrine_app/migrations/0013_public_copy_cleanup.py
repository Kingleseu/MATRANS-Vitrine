from django.db import migrations


def clean_seeded_copy(apps, schema_editor):
    Activite = apps.get_model('vitrine_app', 'Activite')
    Partenaire = apps.get_model('vitrine_app', 'Partenaire')
    database = schema_editor.connection.alias
    replacements = (
        (
            'Caristes & chariots élévateurs',
            'Les caristes interviennent sur les plateformes, dans les centres de distribution et aux points de chargement. La lettre commerciale décrit notamment leur déploiement en usine et au centre de Meferco.',
            'Les caristes interviennent en usine, sur les plateformes et dans les centres de distribution pour assurer le chargement et le déchargement des marchandises.',
        ),
        (
            'Centres & plateformes',
            'L’expérience présentée par MATRANS couvre des centres à Kinshasa et en province. La carte publique montre les centres connus ; leur position exacte reste à confirmer dans le studio.',
            'MATRANS intervient dans des centres de distribution à Kinshasa et en province. La carte présente les centres connus avec des positions indicatives.',
        ),
    )
    for title, old_copy, new_copy in replacements:
        Activite.objects.using(database).filter(
            titre=title,
            description_complete=old_copy,
        ).update(description_complete=new_copy)
    Partenaire.objects.using(database).filter(
        nom='BRACONGO',
        description='Collaboration présentée dans le profil commercial MATRANS (2026).',
    ).update(description='Collaboration dans les opérations de distribution et de manutention.')


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0012_alter_centrevitrine_zone_carte')]
    operations = [migrations.RunPython(clean_seeded_copy, migrations.RunPython.noop)]
