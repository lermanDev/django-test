from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload, name="upload"),
    path("upload_excel", views.UploadPhoneBookView.as_view(), name="upload_excel"),
]
