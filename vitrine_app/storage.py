from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateApplicationStorage(FileSystemStorage):
    def __init__(self):
        location = getattr(settings, 'PRIVATE_MEDIA_ROOT', settings.BASE_DIR / 'private_media')
        super().__init__(location=location, base_url=None)
