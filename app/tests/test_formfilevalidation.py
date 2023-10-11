from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from excel_upload.forms import Excelform

import pandas as pd
import io


class PhoneBookFormTest(TestCase):
    def setUp(self):
        pass

    def get_excel_file_from_dict(self, data):
        df = pd.DataFrame(data)

        # Create an Excel file from the DataFrame
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        return excel_file

    def test_valid_file(self):
        excel_file = self.get_excel_file_from_dict(
            {
                "full_name": ["John Doe"],
                "primary_number": ["+1 (123) 456-7890"],
                "secondary_number": ["+1 (987) 654-3210"],
            }
        )
        file_dict = {
            "file_upload": SimpleUploadedFile("test_valid.xlsx", excel_file.read())
        }
        form = Excelform(files=file_dict)
        assert form.is_valid()

    def test_not_valid_filetype_name(self):
        excel_file = self.get_excel_file_from_dict(
            {
                "full_name": ["John Doe"],
                "primary_number": ["+1 (123) 456-7890"],
                "secondary_number": ["+1 (987) 654-3210"],
            }
        )
        invalid_extension = "xls"
        file_dict = {
            "file_upload": SimpleUploadedFile(
                "test_valid." + invalid_extension, excel_file.read()
            )
        }
        form = Excelform(files=file_dict)

        self.assertFalse(form.is_valid())
        self.assertIn("file_upload", form.errors.keys())

        self.assertEqual(
            form.errors["file_upload"][0],
            "File extension “"
            + invalid_extension
            + "” is not allowed. Allowed extensions are: xlsx.",
        )

    def test_empty_rows(self):
        excel_file = self.get_excel_file_from_dict(
            {
                "full_name": ["John Doe"],
                "primary_number": ["+1 (123) 456-7890"],
                "secondary_number": [""],
            }
        )
        file_dict = {
            "file_upload": SimpleUploadedFile("test_valid.xlsx", excel_file.read())
        }
        form = Excelform(files=file_dict)
        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["__all__"][0],
            "Empty data found in rows: [0]. Each row must contain a full name, a primary number, and a secondary number.",
        )

    def test_invalid_numbers(self):
        excel_file = self.get_excel_file_from_dict(
            {
                "full_name": ["John Doe"],
                "primary_number": ["+1 (123) 456-7890"],
                "secondary_number": ["+1 (987*54-3210"],
            }
        )
        file_dict = {
            "file_upload": SimpleUploadedFile("test_valid.xlsx", excel_file.read())
        }
        form = Excelform(files=file_dict)
        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["__all__"][0],
            "Invalid phone number format found in rows: [0].",
        )

    # duplicates can't be on same column neither on databse
    # def test_validate_duplicates(self):
    #     excel_file = self.get_excel_file_from_dict(
    #         {
    #             "full_name": ["John Doe"],
    #             "primary_number": ["+1 (123) 456-7890", "+1 (123) 456-7890"],
    #             "secondary_number": ["+1 (987*54-3210", "+1 (123) 456-7890"],
    #         }
    #     )
    #     file_dict = {
    #         "file_upload": SimpleUploadedFile("test_valid.xlsx", excel_file.read())
    #     }
    #     form = Excelform(files=file_dict)
    #     self.assertFalse(form.is_valid())

    #     self.assertEqual(
    #         form.errors["__all__"][0],
    #         "Invalid phone number format found in rows: [0].",
    #     )
