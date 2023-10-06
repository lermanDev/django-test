from django.test import TestCase
from django.core.exceptions import ValidationError
from .helpers.validators import FileValidator

import pandas as pd
import magic
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile


class FileValidatorTests(TestCase):
    file_content = open("/app/files/test_xlsx_good_clean.xlsx", "rb")
    excel_file = SimpleUploadedFile(
        "test_file_base.xlsx",
        file_content.read(),
        content_type="application/vnd.ms-excel",
    )

    @mock.patch("magic.from_buffer", return_value=excel_file)
    @mock.patch(
        "pandas.read_excel",
        return_value=pd.DataFrame(
            {
                "full_name": ["John Doe"],
                "primary_number": ["+1 (123) 456-7890"],
                "secondary_number": ["+1 (987) 654-3210"],
            }
        ),
    )
    def test_valid_file(self, mock_from_buffer, mock_read_excel):
        # Creating an instance of FileValidator
        validator = FileValidator(content_types=["application/vnd.ms-excel"])

        # Validating the file
        validator(mock_read_excel.return_value)

        # Asserting that no validation errors were raised
        assert not ValidationError
