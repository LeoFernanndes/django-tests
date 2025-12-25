import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from organizations_management.helpers import generate_download_presigned_url
from organizations_management.models import Organization


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
    IMAGE = "image", _("Image")
    VIDEO = "video", _("Video")
    TEXT = "text", _("Text")


class MimeTypechoices(models.TextChoices):
    # Documents
    PDF = 'application/pdf', _('Adobe PDF (.pdf)')
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', _('Microsoft Word (.docx)')
    TXT = 'text/plain', _('Plain Text (.txt)')
    CSV = 'text/csv', _('Comma Separated Values (.csv)')
    XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', _('Microsoft Excel (.xlsx)')
    
    # Images
    JPG = 'image/jpeg', _('JPEG Image (.jpg/.jpeg)')
    PNG = 'image/png', _('Portable Network Graphics (.png)')
    GIF = 'image/gif', _('Graphics Interchange Format (.gif)')
    SVG = 'image/svg+xml', _('Scalable Vector Graphics (.svg)')
    WEBP = 'image/webp', _('WebP Image (.webp)')
    
    # Audio/Video
    MP4 = 'video/mp4', _('MPEG-4 Video (.mp4)')
    MP3 = 'audio/mpeg', _('MPEG-3 Audio (.mp3)')
    WAV = 'audio/wav', _('Waveform Audio (.wav)')
    
    # Archive/Compressed
    ZIP = 'application/zip', _('Zip Compressed Archive (.zip)')
    GZIP = 'application/gzip', _('Gzip Archive (.gz)')
    
    # Code/Web
    HTML = 'text/html', _('HyperText Markup Language (.html)')
    JSON = 'application/json', _('JavaScript Object Notation (.json)')
    XML = 'application/xml', _('Extensible Markup Language (.xml)')


class File(models.Model):
    id = PrefixedIDField(max_length=255, primary_key=True, prefix="file")
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, choices=MimeTypechoices.choices, default=MimeTypechoices.PDF)
    bucket = models.CharField(max_length=255)
    location = models.TextField()
    organization = models.ForeignKey(to=Organization, null=True, on_delete=models.CASCADE)

    def generate_download_presigned_url(self, expiration=60):
        return generate_download_presigned_url(bucket_name=self.bucket, location=self.location, expiration=expiration)
