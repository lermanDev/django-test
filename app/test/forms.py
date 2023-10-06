from django import forms
from .models import File


class Excelform(forms.ModelForm):
    class Meta:
        model = File
        fields = ("file_upload",)
        widgets = {
            "file_upload": forms.FileInput(
                attrs={
                    "accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
            )
        }
