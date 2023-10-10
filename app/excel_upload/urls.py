from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadPhoneBookView.as_view(), name="upload"),
    path("success", views.BookListView.as_view(), name="success"),
]
