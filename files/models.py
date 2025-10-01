import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from organizations_management.helpers import generate_download_presigned_url


class PrefixedIDField(models.CharField):
    def __init__(self, prefix='PRE', *args, **kwargs):
        self.prefix = prefix
        kwargs['max_length'] = kwargs.get('max_length', 255)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if add:
            _uuid = uuid.uuid4()
            value = f'{self.prefix}-{_uuid}'
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


class FileTypeChoices(models.TextChoices):
    IMAGE = "IMAGE", _("Image")
    VIDEO = "VIDEO", _("Video")


class File(models.Model):
    id = PrefixedIDField(max_length=255, primary_key=True, prefix="file")
    filename = models.TextField()
    filetype = models.CharField(max_length=50, choices=FileTypeChoices)
    bucket = models.CharField(max_length=255)
    location = models.TextField()

    def generate_download_presigned_url(self, expiration=60):
        return generate_download_presigned_url(bucket_name=self.bucket, location=self.location, expiration=expiration)