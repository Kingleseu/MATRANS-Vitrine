from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('activites/', views.activites, name='activites'),
    path('partenaires/', views.partenaires, name='partenaires'),
    path('carrieres/', views.carrieres, name='carrieres'),
    path('carrieres/<int:pk>/', views.offre_detail, name='offre_detail'),
    path('evenements/', views.evenements, name='evenements'),
    path('evenements/<int:pk>/', views.evenement_detail, name='evenement_detail'),
    path('contact/', views.contact, name='contact'),
    path('gestion-vitrine/', include('vitrine_app.backoffice_urls')),
]
