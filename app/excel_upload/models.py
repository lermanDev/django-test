from django.db import models
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.contrib.auth.models import User

file_validator = FileExtensionValidator(allowed_extensions=["xlsx"])


class File(models.Model):
    filename = models.CharField(max_length=250)
    file_upload = models.FileField(upload_to="files/", validators=[file_validator])
    upload_date = models.DateField(default=datetime.now)

    def __str__(self):
        return self.filename


class PhonebookEntry(models.Model):
    full_name = models.CharField(max_length=100)
    primary_number = models.CharField(
        max_length=20, blank=False, null=False, unique=True
    )
    secondary_number = models.CharField(
        max_length=20, blank=False, null=False, unique=True
    )
    file = models.ForeignKey(File, null=True, on_delete=models.CASCADE)
    date_add = models.DateField(default=datetime.now)

    def __str__(self):
        return self.full_name
