import magic
import pandas as pd

from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from .functions import validate_row_numbers


@deconstructible
class FileValidator(object):

    # TODO: Normalize before Validate
        
    error_messages = {
        'rows_w_duplicates': 'Rows %(rows_w_duplicates)s contains duplicate phone numbers: Each row must be unique.',
        'empty_rows': 'Rows %(empty_rows)s contains empty data: Each row must contain a full name, a primary number and a secondary number.',
        'missing_columns': ("Missing required columns: %(missing_columns)s."),
        'invalid_phones_rows': 'Columns %(invalid_phones_rows)s contains invalid phone number format',
        'content_type': "Files of type %(content_type)s are not supported."
    }

    def __init__(self, content_types=()):
        self.content_types = content_types

    def __call__(self, data):

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)

            if content_type not in self.content_types:
                params = { 'content_type': content_type }
                raise ValidationError(self.error_messages['content_type'],
                                   'content_type', params)
            
            data = pd.read_excel(data.read())

            required_columns = ['full_name', 'primary_number', 'secondary_number']
            missing_columns = [col for col in required_columns if col not in data.columns]

            if missing_columns:
                params = { 'missing_columns': missing_columns }
                raise ValidationError(self.error_messages['missing_columns'],
                                    'missing_columns', params)
            
            nan_rows = data.isna().any(axis=1)
            empty_rows = [val + 2 for val in list(nan_rows.index[nan_rows])]

            if empty_rows:
                params = { 'empty_rows': empty_rows }
                raise ValidationError(self.error_messages['empty_rows'],
                                'empty_rows', params)
            
            validated_rows = data.apply(validate_row_numbers, axis=1)
            invalid_phones_rows = [val + 2 for val in list(validated_rows.index[~validated_rows])]
            
            if invalid_phones_rows:
                params = { 'invalid_phones_rows': invalid_phones_rows }
                raise ValidationError(self.error_messages['invalid_phones_rows'],
                                'invalid_phones_rows', params)
            
            column_list = ['primary_number', 'secondary_number']


            duplicates = set()
            for column in column_list:
                duplicated_rows = [index+2 for index in data[data[column].duplicated()].index]
                duplicates.update(duplicated_rows)

            if duplicates:
                params = {'rows_w_duplicates': list(duplicates)}
                raise ValidationError(self.error_messages['rows_w_duplicates'],
                                'rows_w_duplicates', params)
            