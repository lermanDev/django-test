from django.shortcuts import render
from .forms import Excelform
from .models import PhonebookEntry
from .helpers.functions import normalize_phone_number
from django.db.utils import IntegrityError

def upload(request):
    import pandas as pd

    form = Excelform()
    duplicates_index_list = []

    if request.method == "POST":
        file_form = Excelform(request.POST, request.FILES)
        raw_file= request.FILES
        if file_form.is_valid():
            data = request.FILES['file_upload']

            df = pd.read_excel(data)
            for index, line in df.iterrows():
                try:
                    phonebook_entry = PhonebookEntry(
                        full_name=line['full_name'],
                        primary_number=normalize_phone_number(line['primary_number']),
                        secondary_number=normalize_phone_number(line['secondary_number'])
                    )
                    phonebook_entry.save()
                except IntegrityError as e:
                    duplicates_index_list.append(
                        {
                            'full_name': line['full_name'],
                            'primary_number': normalize_phone_number(line['primary_number']),
                            'secondary_number': normalize_phone_number(line['secondary_number'])
                        }
                    )
                    continue
                   
            file_form.save(commit=True)

            if not duplicates_index_list:
                phone_book_list = PhonebookEntry.objects.all()
                return render(request, 'success.html', {'phone_book_list': phone_book_list})
            
            return render(request, 'failed.html', {"duplicates_index_list": duplicates_index_list})
        form = file_form
    
    return render(request, 'upload_form.html', {'form': form})