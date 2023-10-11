from django.test import TestCase

from excel_upload.models import PhonebookEntry


class PhoneBookDBTest(TestCase):
    def setUp(self):
        pb_dict = {
            "full_name": "John Doe",
            "primary_number": "+1 (123) 456-7890",
            "secondary_number": "+11234567890",
        }
        PhonebookEntry.objects.create(**pb_dict)

    def test_phonebookentry_creation(self):
        pb_entry = PhonebookEntry.objects.get(primary_number="+1 (123) 456-7890")
        assert pb_entry.full_name == "John Doe"
        assert pb_entry.secondary_number != "+11254567890"
