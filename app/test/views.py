from django.shortcuts import render
from .forms import Excelform
from django.db.utils import IntegrityError
import pandas as pd
from django.utils.safestring import mark_safe
from .models import File, PhonebookEntry
from django.views.generic import CreateView
from django.urls import reverse_lazy


def upload(request):
    form = Excelform()

    if request.method == "POST":
        file_form = Excelform(request.POST, request.FILES)

        if file_form.is_valid():
            file_form.save(commit=True)
            df = pd.DataFrame(list(PhonebookEntry.objects.all().values()))
            return render(
                request,
                "success.html",
                {"phone_book_html": mark_safe(df.to_html())},
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


class UploadPhoneBookView(CreateView):
    model = File
    form_class = Excelform
    success_url = reverse_lazy("upload_excel")
    template_name = "upload_form.html"
