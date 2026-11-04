from django.db import migrations, models

import vitrine_app.home_sections


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0025_textes_accueil')]

    operations = [
        migrations.AddField(
            model_name='sitecontent',
            name='home_section_order',
            field=models.JSONField(
                default=vitrine_app.home_sections.default_home_sections,
                verbose_name='Ordre des sections de l’accueil',
            ),
        ),
    ]
