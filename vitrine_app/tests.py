import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Activite, CentreVitrine, Evenement, OffreEmploi, Partenaire, SiteContent


class PageVisibilityTests(TestCase):
    databases = {'default', 'vitrine_db'}

    @classmethod
    def setUpTestData(cls):
        cls.site = SiteContent.objects.first() or SiteContent.objects.create()
        cls.offer = OffreEmploi.objects.create(
            titre='Cariste', description='Manutention', profil_recherche='Expérience',
        )
        cls.event = Evenement.objects.create(
            titre='Rencontre', resume='Rencontre sur le terrain',
            description='Présentation', date_debut=timezone.now(), publie=True,
        )
        group = Group.objects.create(name='Editeurs vitrine')
        cls.editor = get_user_model().objects.create_user(
            username='editeur-test', password='mot-de-passe-test',
        )
        cls.editor.groups.add(group)

    def test_hidden_pages_disappear_from_navigation_and_return_404(self):
        pages = (
            ('page_about_visible', 'a_propos'),
            ('page_activities_visible', 'activites'),
            ('page_partners_visible', 'partenaires'),
            ('page_events_visible', 'evenements'),
            ('page_careers_visible', 'carrieres'),
            ('page_contact_visible', 'contact'),
        )
        for field, name in pages:
            with self.subTest(page=name):
                setattr(self.site, field, False)
                self.site.save(update_fields=[field])
                url = reverse(name)
                self.assertEqual(self.client.get(url).status_code, 404)
                homepage = self.client.get(reverse('home'))
                self.assertEqual(homepage.status_code, 200)
                self.assertNotContains(homepage, f'href="{url}"')
                setattr(self.site, field, True)
                self.site.save(update_fields=[field])
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_three_page_home_keeps_activities_clients_and_map_visible(self):
        self.site.page_about_visible = False
        self.site.page_activities_visible = False
        self.site.page_partners_visible = False
        self.site.page_careers_visible = False
        self.site.page_events_visible = True
        self.site.page_contact_visible = True
        self.site.save()
        Activite.objects.create(
            titre='Manutention mécanisée',
            description_courte='Chargement et déchargement des marchandises.',
            description_complete='Activité sur site.',
            ordre=2,
        )
        Partenaire.objects.create(nom='BRACONGO', publie=True)
        CentreVitrine.objects.create(
            code='test-gombe', nom='CD Gombe', ville='Gombe', province='Kinshasa',
            latitude=-4.31, longitude=15.31, publie=True,
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        for content in (
            'Nos activités', 'Manutention mécanisée', 'Caristes &amp; chariots élévateurs',
            'Nos clients', 'Ils nous font confiance.', 'BRACONGO', 'CD Gombe',
            'data-home-zone=', '+200', '≈ 300 000', 'Au <em>cœur</em> de vos opérations',
            'est une entreprise spécialisée dans les opérations de manutention, avec une extension naturelle vers le transport.',
            'Nous mettons à votre disposition un encadrement et un suivi opérationnel rigoureux',
            'Matrans SARL déploie ses activités en RDC sur',
            'Explorez la carte pour découvrir les centres de chaque zone',
        ):
            self.assertContains(response, content)
        self.assertNotContains(response, 'Expérience partenaire')
        self.assertNotContains(response, 'Assurer la continuité des opérations')
        self.assertNotContains(response, 'Mettre des équipes formées et supervisées au service des opérations')
        self.assertNotContains(response, 'Rigueur, discipline et sécurité au quotidien.')
        html = response.content.decode()
        self.assertEqual(html.count('data-hero-slide'), 3)
        self.assertNotIn('data-hero-control=', html)
        self.assertNotIn('hero-visual-note', html)
        self.assertIn('La bannière comprend des visuels d’illustration.', html)
        self.assertIn('hero-cariste-naturel.webp', html)
        self.assertIn('hero-equipe-naturelle.webp', html)
        self.assertIn('class="hero-image is-active"', html)
        self.assertLess(html.index('id="carte-accueil"'), html.index('class="home-values"'))
        self.assertLess(html.index('class="home-values"'), html.index('id="nos-activites"'))
        self.assertLess(html.index('id="nos-activites"'), html.index('class="identity-intro"'))
        self.assertLess(html.index('class="identity-intro"'), html.index('id="partners-title"'))
        self.assertEqual(html.count('Notre impact, en chiffres</h3>'), 1)
        self.assertNotIn('terrain-cariste-casiers-matrans.jpg', html)
        self.assertEqual(html.count('<span class="copy-accent">sécurité, réduction des incidents et régularité des effectifs</span>'), 1)
        self.assertEqual(html.count('Nous mettons à votre disposition un encadrement et un suivi opérationnel rigoureux'), 1)
        for page in ('a_propos', 'activites', 'partenaires', 'carrieres'):
            self.assertEqual(self.client.get(reverse(page)).status_code, 404)
        for page in ('evenements', 'contact'):
            self.assertEqual(self.client.get(reverse(page)).status_code, 200)

    def test_custom_mission_escapes_editorial_html(self):
        self.site.mission = '<script>alert(1)</script> sécurité, réduction des incidents et régularité des effectifs'
        self.site.save(update_fields=['mission'])
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_editor_can_reorder_home_sections_and_public_page_follows(self):
        url = reverse('vitrine_admin:home_sections_order')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.editor)
        page = self.client.get(url)
        self.assertContains(page, 'Ordre de l’accueil')
        self.assertContains(page, 'Au cœur de vos opérations')
        self.assertEqual(self.client.post(url, {'section': 'unknown', 'direction': 'up'}).status_code, 400)
        self.assertRedirects(self.client.post(url, {'section': 'identity', 'direction': 'up'}), url)
        self.site.refresh_from_db()
        self.assertEqual(self.site.home_section_order[:4], ['map', 'values', 'identity', 'activities'])
        html = self.client.get(reverse('home')).content.decode()
        self.assertLess(html.index('class="identity-intro"'), html.index('id="nos-activites"'))

    def test_hidden_careers_and_events_block_direct_detail_pages(self):
        self.site.page_careers_visible = False
        self.site.page_events_visible = False
        self.site.save(update_fields=['page_careers_visible', 'page_events_visible'])
        self.assertEqual(self.client.get(reverse('offre_detail', args=[self.offer.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('evenement_detail', args=[self.event.pk])).status_code, 404)

    def test_editor_can_toggle_pages_without_deleting_content(self):
        url = reverse('vitrine_admin:page_visibility')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {
            'page_about_visible': 'on', 'page_activities_visible': 'on',
            'page_partners_visible': 'on', 'page_careers_visible': 'on',
            'page_contact_visible': 'on',
        })
        self.assertRedirects(response, url)
        self.site.refresh_from_db()
        self.assertFalse(self.site.page_events_visible)
        self.assertEqual(Evenement.objects.count(), 1)
        response = self.client.post(url, {
            'page_about_visible': 'on', 'page_activities_visible': 'on',
            'page_partners_visible': 'on', 'page_events_visible': 'on',
            'page_careers_visible': 'on', 'page_contact_visible': 'on',
        })
        self.assertRedirects(response, url)
        self.site.refresh_from_db()
        self.assertTrue(self.site.page_events_visible)


class StudioAccountTests(TestCase):
    databases = {'default', 'vitrine_db'}
    setup_token = 'code-initialisation-test-2026-assez-long'

    @override_settings(VITRINE_SETUP_TOKEN='')
    def test_initial_account_form_is_closed_without_setup_code(self):
        self.assertEqual(self.client.get(reverse('vitrine_admin:initial_account')).status_code, 404)
        login_page = self.client.get(reverse('vitrine_admin:connexion'))
        self.assertNotContains(login_page, 'Créer le premier accès')

    @override_settings(VITRINE_SETUP_TOKEN=setup_token)
    def test_initial_form_keeps_https_csrf_protection_usable(self):
        url = reverse('vitrine_admin:initial_account')
        client = Client(enforce_csrf_checks=True)
        page = client.get(url, secure=True)
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, 'name="referrer" content="no-referrer"')
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode()).group(1)
        response = client.post(url, {
            'csrfmiddlewaretoken': token,
            'access_code': 'mauvais-code',
            'username': 'nouveau-responsable',
            'email': 'responsable@example.com',
            'password1': 'MotDePasseLongEtUnique2026!',
            'password2': 'MotDePasseLongEtUnique2026!',
        }, secure=True, HTTP_REFERER='https://testserver' + url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'installation invalide.')

    @override_settings(VITRINE_SETUP_TOKEN=setup_token)
    def test_first_account_requires_code_and_closes_after_creation(self):
        url = reverse('vitrine_admin:initial_account')
        self.assertEqual(self.client.get(url).status_code, 200)
        data = {
            'username': 'responsable-vitrine', 'email': 'responsable@example.com',
            'password1': 'MotDePasseLongEtUnique2026!',
            'password2': 'MotDePasseLongEtUnique2026!',
            'access_code': 'mauvais-code',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username=data['username']).exists())
        data['access_code'] = self.setup_token
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('vitrine_admin:dashboard'))
        user = get_user_model().objects.get(username=data['username'])
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(data['password1']))
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get(reverse('vitrine_admin:dashboard')).status_code, 200)

    def test_only_administrator_can_create_editor_account(self):
        User = get_user_model()
        group = Group.objects.create(name='Editeurs vitrine')
        editor = User.objects.create_user(username='editor', password='mot-de-passe-editeur')
        editor.groups.add(group)
        admin = User.objects.create_superuser(
            username='admin-vitrine', email='admin@example.com', password='mot-de-passe-admin',
        )
        url = reverse('vitrine_admin:account_create')
        self.client.force_login(editor)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(admin)
        response = self.client.post(url, {
            'username': 'nouvel-editeur', 'email': 'editeur@example.com',
            'password1': 'AutreMotDePasseLong2026!',
            'password2': 'AutreMotDePasseLong2026!',
        })
        self.assertRedirects(response, reverse('vitrine_admin:accounts'))
        created = User.objects.get(username='nouvel-editeur')
        self.assertTrue(created.groups.filter(name='Editeurs vitrine').exists())
        self.assertFalse(created.is_superuser)
