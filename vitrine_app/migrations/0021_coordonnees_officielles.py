from django.db import migrations, models


ADRESSE = (
    '4, avenue de la Justice, Commune de la Gombe, Kinshasa, '
    'République démocratique du Congo'
)
EMAIL = 'contact@matrans-rdc.com'
TELEPHONE = '+243 982 186 167'


def actualiser_coordonnees(apps, schema_editor):
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    SiteContent.objects.using(schema_editor.connection.alias).update(
        contact_address=ADRESSE,
        contact_email=EMAIL,
        contact_phone=TELEPHONE,
    )


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0020_raison_etre_externalisation')]

    operations = [
        migrations.AlterField(
            model_name='sitecontent',
            name='contact_address',
            field=models.CharField(blank=True, default=ADRESSE, max_length=255),
        ),
        migrations.AlterField(
            model_name='sitecontent',
            name='contact_email',
            field=models.EmailField(blank=True, default=EMAIL, max_length=254),
        ),
        migrations.AlterField(
            model_name='sitecontent',
            name='contact_phone',
            field=models.CharField(blank=True, default=TELEPHONE, max_length=50),
        ),
        migrations.RunPython(actualiser_coordonnees, migrations.RunPython.noop),
    ]
