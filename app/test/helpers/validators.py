import magic
import pandas as pd

from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from .functions import *


@deconstructible
class FileValidator(object):
    VALIDATION_ERRORS = {
        "rows_with_duplicates": "Duplicate phone numbers found in rows %(rows_with_duplicates)s. Each row must be unique.",
        "empty_rows": "Empty data found in rows %(empty_rows)s. Each row must contain a full name, a primary number, and a secondary number.",
        "missing_columns": "Missing required columns: %(missing_columns)s.",
        "invalid_phone_rows": "Invalid phone number format found in rows %(invalid_phone_rows)s.",
        "content_type": "Files of type %(content_type)s are not supported.",
        "wrong_columns": "Wrong column order, expected: %(columns)s.",
    }

    REQUIRED_COLUMNS = ["full_name", "primary_number", "secondary_number"]

    def __init__(self, content_types=()):
        self.content_types = content_types

    def _handle_validation_error(self, error_type, error_params):
        raise ValidationError(
            self.VALIDATION_ERRORS[error_type], error_type, error_params
        )

    def validate_phones(self, data):
        # Invalid phones Validation
        validated_rows = data.apply(validate_row_numbers, axis=1)
        invalid_phone_rows = [
            val + 2 for val in list(validated_rows.index[~validated_rows])
        ]
        if invalid_phone_rows:
            self._handle_validation_error(
                "invalid_phone_rows", {"invalid_phone_rows": invalid_phone_rows}
            )

    def validate_column_order(self, data):
        # Check if columns are in the same order
        if not data.columns.tolist() == self.REQUIRED_COLUMNS:
            self._handle_validation_error(
                "wrong_columns", {"columns": self.REQUIRED_COLUMNS}
            )

    def validate_missing_columns(self, data):
        # Missing columns validation
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS if col not in data.columns
        ]
        if missing_columns:
            self._handle_validation_error(
                "missing_columns", {"missing_columns": missing_columns}
            )

    def validate_empty_data(self, data):
        # Empty data Validation
        nan_rows = data.isna().any(axis=1)
        empty_rows = [val + 2 for val in list(nan_rows.index[nan_rows])]
        if empty_rows:
            self._handle_validation_error("empty_rows", {"empty_rows": empty_rows})

    def validate_duplicates(self, data):
        # Duplicates in File Validation
        duplicates = set()
        for column in self.REQUIRED_COLUMNS[1:]:
            duplicated_rows = [
                index + 2 for index in data[data[column].duplicated()].index
            ]
            duplicates.update(duplicated_rows)
        if duplicates:
            self._handle_validation_error(
                "rows_with_duplicates", {"rows_with_duplicates": list(duplicates)}
            )

    def validate_filetype(self, data):
        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)

        if content_type not in self.content_types:
            self._handle_validation_error(
                "content_type", {"content_type": content_type}
            )

    def __call__(self, data):
        if self.content_types:
            self.validate_filetype(data)

            data = pd.read_excel(data.read())

            # Normalize all data
            clean_columns = ["primary_number", "secondary_number"]
            data[clean_columns] = data[clean_columns].map(
                lambda s: normalize_phone_number(s)
            )

            self.validate_phones(data)
            self.validate_column_order(data)
            self.validate_missing_columns(data)
            self.validate_empty_data(data)
            self.validate_duplicates(data)
