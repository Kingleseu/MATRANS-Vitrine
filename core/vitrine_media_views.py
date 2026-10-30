"""Serve only public editorial images from the attached media disk.

Candidate CVs are stored outside MEDIA_ROOT and are served solely by the
authenticated back-office download view.
"""

import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET


@require_GET
def public_image(request, path):
    root = Path(settings.MEDIA_ROOT).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise Http404
    content_type, _ = mimetypes.guess_type(target.name)
    if content_type not in {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}:
        raise Http404
    return FileResponse(target.open('rb'), content_type=content_type)
