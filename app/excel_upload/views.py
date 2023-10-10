from django.shortcuts import render
from .forms import Excelform
from django.db.utils import IntegrityError
import pandas as pd
from django.utils.safestring import mark_safe
from .models import File, PhonebookEntry
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.shortcuts import redirect


class BookListView(ListView):
    model = PhonebookEntry
    template_name = "success.html"
    context_object_name = "success"

    def get(self, request):
        df = pd.DataFrame(list(PhonebookEntry.objects.all().values()))
        return render(
            request,
            "success.html",
            {"phone_book_html": mark_safe(df.to_html())},
        )


class UploadPhoneBookView(CreateView):
    model = File
    form_class = Excelform
    success_url = reverse_lazy("")
    template_name = "upload_form.html"

    def post(self, request):
        file_form = Excelform(request.POST, request.FILES)

        if file_form.is_valid():
            file_form.save(commit=True)
            return redirect("success")
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
