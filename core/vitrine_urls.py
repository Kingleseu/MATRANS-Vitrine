"""URL set exposed by the standalone showcase deployment."""

from django.urls import include, path, re_path

from . import vitrine_media_views


urlpatterns = [
    path('', include('vitrine_app.urls')),
    re_path(r'^media/(?P<path>(?:vitrine|activites|partenaires)/.+)$', vitrine_media_views.public_image),
]
