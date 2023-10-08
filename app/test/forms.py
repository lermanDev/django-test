from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from .models import File, PhonebookEntry
import magic, phonenumbers
import pandas as pd
from django.db.models import Q


class Excelform(forms.ModelForm):
    class Meta:
        model = File
        fields = ("file_upload",)
        widgets = {
            "file_upload": forms.FileInput(
                attrs={
                    "accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
            )
        }

    def _handle_validation_error(self, error_type, error_params):
        VALIDATION_ERRORS = {
            "rows_with_duplicates": "Duplicate phone numbers found in rows: %(rows_with_duplicates)s. Each row must be unique.",
            "rows_with_duplicates_db": "Duplicate phone numbers found in database in rows: %(rows_with_duplicates_db)s. Each row must be unique.",
            "empty_rows": "Empty data found in rows: %(empty_rows)s. Each row must contain a full name, a primary number, and a secondary number.",
            "missing_columns": "Missing required columns: %(missing_columns)s.",
            "invalid_phone_rows": "Invalid phone number format found in rows: %(invalid_phone_rows)s.",
            "content_type": "Files of type %(content_type)s are not supported.",
            "wrong_columns": "Wrong column order, expected: %(columns)s.",
        }
        raise ValidationError(
            VALIDATION_ERRORS[error_type], code=error_type, params=error_params
        )

    def validate_filetype(self, data, valid_content_type):
        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)

        if content_type not in valid_content_type:
            self._handle_validation_error(
                "content_type", {"content_type": content_type}
            )

    def validate_phones(self, data, data_normalized, action_columns):
        self.cleaned_data["clean_dict"] = data.fillna("").style.map(
            lambda cell: "background-color:#f8d7da"
            if pd.isna(self.normalize_phone_number(cell))
            else "",
            subset=pd.IndexSlice[:, action_columns],
        )

        data_nan = data_normalized.isna()
        nan_rows = data_nan.any(axis=1)
        invalid_rows = [val for val in list(nan_rows.index[nan_rows])]
        if invalid_rows:
            self.cleaned_data["error_dict"] = data_nan
            self._handle_validation_error(
                "invalid_phone_rows", {"invalid_phone_rows": invalid_rows}
            )

    def validate_column_order(self, data, required_columns):
        styled_data = data.style
        required_error_list = []
        selector_list = []

        for i, column in enumerate(required_columns):
            if data.columns.get_loc(column) != i:
                required_error_list.append(column)
                selector_list.append(
                    {
                        "selector": f"th:nth-child({i + 2})",
                        "props": [("background-color", "#f8d7da")],
                    }
                )

        # Define a custom styling function to highlight required columns
        def highlight_required_cols(s, required_error_list):
            if s.name in required_error_list:
                return ["background-color: #f8d7da"] * s.shape[0]

        styled_data.apply(
            highlight_required_cols, required_error_list=required_error_list, axis=0
        ).set_table_styles(selector_list)

        self.cleaned_data["clean_dict"] = styled_data
        # Check if columns are in the same order
        if not data.columns.tolist() == required_columns:
            self._handle_validation_error(
                "wrong_columns", {"columns": required_columns}
            )

    def validate_missing_columns(self, data, required_columns):
        # Missing columns validation
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            self._handle_validation_error(
                "missing_columns", {"missing_columns": missing_columns}
            )

    def validate_empty_data(self, data):
        # Empty data Validation
        data_nan = data.isna()

        self.cleaned_data["clean_dict"] = data.fillna("").style.map(
            lambda cell: "background-color:#f8d7da" if pd.isna(cell) else ""
        )
        nan_rows = data_nan.any(axis=1)
        empty_rows = [val for val in list(nan_rows.index[nan_rows])]
        if empty_rows:
            self._handle_validation_error("empty_rows", {"empty_rows": empty_rows})

    def validate_duplicates_db(self, data, no_duplicate_columns):
        # Duplicates in File Validation
        duplicates_db = set()
        styled_data = data.style

        def highlight_duplicates_db(column, duplicated_db_rows):
            return [
                "background-color: #f8d7da" if v else "" for v in duplicated_db_rows
            ]

        for column in no_duplicate_columns:
            kwargs_in = {"{0}__{1}".format(column, "in"): data[column]}
            phonebook_duplicates = PhonebookEntry.objects.filter(Q(**kwargs_in))

            if phonebook_duplicates.exists():
                duplicated_db_rows_index = [
                    index
                    for index in data[
                        data[column].isin(
                            phonebook_duplicates.values_list(column, flat=True)
                        )
                    ].index
                ]

                duplicated_db_rows = [
                    index
                    for index in data[column].isin(
                        phonebook_duplicates.values_list(column, flat=True)
                    )
                ]

                styled_data.apply(
                    highlight_duplicates_db,
                    duplicated_db_rows=duplicated_db_rows,
                    subset=[column],
                )
                duplicates_db.update(duplicated_db_rows_index)

        self.cleaned_data["clean_dict"] = styled_data

        if duplicates_db:
            self._handle_validation_error(
                "rows_with_duplicates_db",
                {"rows_with_duplicates_db": list(duplicates_db)},
            )

    def validate_duplicates(self, data, no_duplicate_columns):
        duplicates = set()

        # Define a function to apply the background color to duplicated values
        def highlight_duplicates(column):
            duplicated_rows = column.duplicated()
            return ["background-color: #f8d7da" if v else "" for v in duplicated_rows]

        styled_data = data.style

        for column in no_duplicate_columns:
            # Apply the styling to the specified column
            styled_data.apply(highlight_duplicates, subset=[column])
            duplicated_rows = [index for index in data[data[column].duplicated()].index]
            duplicates.update(duplicated_rows)

        if duplicates:
            self.cleaned_data["clean_dict"] = styled_data
            self._handle_validation_error(
                "rows_with_duplicates", {"rows_with_duplicates": list(duplicates)}
            )

    def normalize_phone_number(self, phone_number_str: str):
        try:
            phone_number_str = "".join(
                char for char in str(phone_number_str) if char.isdigit() or char in "+"
            )
            parsed_number = phonenumbers.parse(phone_number_str.replace(" ", ""), None)
            if not phonenumbers.is_possible_number(parsed_number):
                return None
            normalized_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            return str(normalized_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return None

    def clean(self):
        self.cleaned_data["error_dict"] = {}

        required_columns = ["full_name", "primary_number", "secondary_number"]
        action_columns = ["primary_number", "secondary_number"]
        valid_filetype = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        file_data = self.cleaned_data.get("file_upload")
        self.validate_filetype(file_data, valid_filetype)

        data = pd.read_excel(file_data.read())
        self.cleaned_data["clean_dict"] = data
        # self.validate_empty_data(data)

        data_normalized = data[action_columns].map(
            lambda s: self.normalize_phone_number(s)
        )

        self.validate_phones(data, data_normalized, action_columns)

        # Normalize all data
        data[action_columns] = data_normalized

        self.cleaned_data["clean_dict"] = data

        self.validate_column_order(data, required_columns)
        self.validate_missing_columns(data, required_columns)
        self.validate_duplicates(data, action_columns)
        self.validate_duplicates_db(data, action_columns)

        self.cleaned_data["clean_data"] = data

        return super().clean()

    def save(self, commit=True):
        m = super(Excelform, self).save(commit=False)

        data = self.cleaned_data["clean_data"]

        for index, line in data.iterrows():
            PhonebookEntry.objects.create(**dict(line))
        if commit:
            m.save()
        return m
