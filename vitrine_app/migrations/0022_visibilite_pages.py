from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0021_coordonnees_officielles')]

    operations = [
        migrations.AddField(
            model_name='sitecontent', name='page_about_visible',
            field=models.BooleanField(default=True, verbose_name='Qui sommes-nous'),
        ),
        migrations.AddField(
            model_name='sitecontent', name='page_activities_visible',
            field=models.BooleanField(default=True, verbose_name='Activités'),
        ),
        migrations.AddField(
            model_name='sitecontent', name='page_partners_visible',
            field=models.BooleanField(default=True, verbose_name='Partenaires'),
        ),
        migrations.AddField(
            model_name='sitecontent', name='page_events_visible',
            field=models.BooleanField(default=True, verbose_name='Événements'),
        ),
        migrations.AddField(
            model_name='sitecontent', name='page_careers_visible',
            field=models.BooleanField(default=True, verbose_name='Carrières et offres d’emploi'),
        ),
        migrations.AddField(
            model_name='sitecontent', name='page_contact_visible',
            field=models.BooleanField(default=True, verbose_name='Contact'),
        ),
    ]
