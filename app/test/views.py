from django.shortcuts import render
from .forms import Excelform
from .models import PhonebookEntry
from django.db.utils import IntegrityError
import pandas as pd
from django.utils.safestring import mark_safe


def save_excel_data(data):
    duplicates_index_list = []
    for index, line in data.iterrows():
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
            duplicates_index_list = save_excel_data(
                file_form.cleaned_data["clean_dict"]
            )
            file_form.save(commit=True)

            if not duplicates_index_list:
                return render(
                    request,
                    "success.html",
                    {"phone_book_list": PhonebookEntry.objects.all()},
                )

            return render(
                request, "failed.html", {"duplicates_index_list": duplicates_index_list}
            )
        form = file_form
        return render(
            request,
            "upload_form.html",
            {
                "form": form,
                "clean_table": mark_safe(
                    file_form.cleaned_data["clean_dict"].to_html()
                ),
                "error_dict": file_form.cleaned_data["error_dict"],
            },
        )

    # print(file_form.cleaned_data["clean_dict"], file_form.cleaned_data["error_dict"])
    return render(
        request,
        "upload_form.html",
        {
            "form": form,
        },
    )
