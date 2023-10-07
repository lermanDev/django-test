from django.shortcuts import render
from .forms import Excelform
from .models import PhonebookEntry
from .helpers.functions import normalize_phone_number
from django.db.utils import IntegrityError
import pandas as pd


def save_excel_data(data):
    df = pd.read_excel(data)
    duplicates_index_list = []
    clean_columns = ["primary_number", "secondary_number"]
    df[clean_columns] = df[clean_columns].map(lambda s: normalize_phone_number(s))

    for index, line in df.iterrows():
        try:
            PhonebookEntry.objects.create(**dict(line))
        except IntegrityError:
            duplicates_index_list.append(dict(line))
            continue
    return duplicates_index_list


def upload(request):
    form = Excelform()
    duplicates_index_list = []

    if request.method == "POST":
        file_form = Excelform(request.POST, request.FILES)

        if file_form.is_valid():
            data = request.FILES["file_upload"]

            duplicates_index_list = save_excel_data(data)
            file_form.save(commit=True)

            if not duplicates_index_list:
                phone_book_list = PhonebookEntry.objects.all()
                return render(
                    request, "success.html", {"phone_book_list": phone_book_list}
                )

            return render(
                request, "failed.html", {"duplicates_index_list": duplicates_index_list}
            )
        form = file_form

    return render(request, "upload_form.html", {"form": form})
