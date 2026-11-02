from django.contrib.auth.views import LogoutView
from django.urls import path

from . import backoffice_views as views

app_name = 'vitrine_admin'

urlpatterns = [
    path('connexion/', views.StudioLoginView.as_view(), name='connexion'),
    path('initialiser/', views.initial_account, name='initial_account'),
    path('deconnexion/', LogoutView.as_view(next_page='vitrine_admin:connexion'), name='deconnexion'),
    path('', views.dashboard, name='dashboard'),
    path('contenu/', views.site_content, name='site_content'),
    path('pages/', views.page_visibility, name='page_visibility'),
    path('mot-de-passe/', views.change_password, name='change_password'),
    path('comptes/', views.accounts_list, name='accounts'),
    path('comptes/nouveau/', views.account_create, name='account_create'),
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('candidatures/', views.applications_list, name='applications'),
    path('candidatures/<int:pk>/', views.application_detail, name='application_detail'),
    path('candidatures/<int:pk>/cv/', views.application_cv, name='application_cv'),
    path('offres/<int:offer_pk>/questions/nouvelle/', views.question_edit, name='question_new'),
    path('offres/<int:offer_pk>/questions/<int:pk>/', views.question_edit, name='question_edit'),
    path('<slug:section>/', views.section_list, name='section_list'),
    path('<slug:section>/nouveau/', views.section_edit, name='section_new'),
    path('<slug:section>/<int:pk>/', views.section_edit, name='section_edit'),
]
