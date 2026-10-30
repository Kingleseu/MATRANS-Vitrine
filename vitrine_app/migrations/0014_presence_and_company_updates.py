from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


NEW_HERO = (
    'Spécialiste de la manutention, MATRANS S.A.R.L. s’appuie sur des équipes '
    'expérimentées et un encadrement rigoureux pour accompagner vos opérations, '
    'avec une ouverture vers le transport de marchandises.'
)


def update_public_content(apps, schema_editor):
    db = schema_editor.connection.alias
    SiteContent = apps.get_model('vitrine_app', 'SiteContent')
    CentreVitrine = apps.get_model('vitrine_app', 'CentreVitrine')
    PresenceVille = apps.get_model('vitrine_app', 'PresenceVille')

    SiteContent.objects.using(db).filter(
        hero_text='Chargement, déchargement et encadrement des caristes et manutentionnaires : des équipes supervisées pour faire avancer vos opérations.'
    ).update(hero_text=NEW_HERO)
    SiteContent.objects.using(db).filter(
        metric_casiers__in=['3 000 000', '3 000 00']
    ).update(metric_casiers='300 000')
    SiteContent.objects.using(db).filter(
        metric_source='Présentation commerciale 2026 et correction du volume quotidien communiquée par MATRANS le 30 octobre 2026'
    ).update(metric_source='Présentation commerciale MATRANS 2026 ; volume quotidien confirmé par MATRANS le 30 octobre 2026')
    SiteContent.objects.using(db).filter(
        contact_email__in=['contact@matrans-rdc.com', '']
    ).update(contact_email='contact@matrans-sarl.com')

    if CentreVitrine.objects.using(db).filter(code='cd-meferco').exists():
        CentreVitrine.objects.using(db).filter(code='cd-limete', nom='CD LIMETE').update(publie=False)
    else:
        CentreVitrine.objects.using(db).filter(code='cd-limete', nom='CD LIMETE').update(
            code='cd-meferco', nom='CD MEFERCO', ville='Limete', province='Kinshasa',
        )

    for order, city, province, latitude, longitude in (
        (1, 'Tshikapa', 'Kasaï', '-6.423100', '20.788800'),
        (2, 'Kananga', 'Kasaï Central', '-5.899000', '22.477800'),
        (3, 'Bandundu', 'Kwilu', '-3.316670', '17.383330'),
    ):
        PresenceVille.objects.using(db).get_or_create(ville=city, defaults={
            'province': province, 'latitude': latitude, 'longitude': longitude,
            'publie': True, 'ordre': order,
        })


class Migration(migrations.Migration):
    dependencies = [('vitrine_app', '0013_public_copy_cleanup')]

    operations = [
        migrations.CreateModel(
            name='PresenceVille',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ville', models.CharField(max_length=120, unique=True, verbose_name='Ville')),
                ('province', models.CharField(max_length=120, verbose_name='Province')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[MinValueValidator(-90), MaxValueValidator(90)])),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[MinValueValidator(-180), MaxValueValidator(180)])),
                ('publie', models.BooleanField(default=False, verbose_name='Visible sur le site')),
                ('ordre', models.PositiveIntegerField(default=0, verbose_name='Ordre d’affichage')),
            ],
            options={'verbose_name': 'Ville d’intervention', 'verbose_name_plural': 'Villes d’intervention', 'ordering': ['ordre', 'ville']},
        ),
        migrations.AddField(
            model_name='contactmessage', name='notification_status',
            field=models.CharField(
                choices=[('non_configure', 'Non configurée'), ('envoye', 'Envoyée'), ('erreur', 'Échec')],
                default='non_configure', max_length=20, verbose_name='Notification e-mail',
            ),
        ),
        migrations.CreateModel(
            name='ContactReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Réponse envoyée')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Envoyée le')),
                ('contact', models.ForeignKey(on_delete=models.CASCADE, related_name='reponses', to='vitrine_app.contactmessage')),
            ],
            options={'verbose_name': 'Réponse à un contact', 'verbose_name_plural': 'Réponses aux contacts', 'ordering': ['sent_at']},
        ),
        migrations.AlterField(
            model_name='sitecontent', name='hero_text', field=models.TextField(default=NEW_HERO),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='metric_casiers',
            field=models.CharField(default='300 000', max_length=30, verbose_name='Manipulations par jour · chiffre'),
        ),
        migrations.AlterField(
            model_name='sitecontent', name='metric_source',
            field=models.CharField(
                default='Présentation commerciale MATRANS 2026 ; volume quotidien confirmé par MATRANS le 30 octobre 2026',
                max_length=220, verbose_name='Source et période des chiffres',
            ),
        ),
        migrations.RunPython(update_public_content, migrations.RunPython.noop),
    ]
