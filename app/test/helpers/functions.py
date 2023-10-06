import phonenumbers


def normalize_phone_number(phone_number_str):
    try:
        # Remove any non-numeric characters
        phone_number_str = "".join(
            char for char in phone_number_str if char.isdigit() or char in "+"
        )
        phone_number_str = phone_number_str.replace("-", " ")

        # Parse the phone number string
        parsed_number = phonenumbers.parse(phone_number_str, None)

        # Check if the number is valid
        if not phonenumbers.is_possible_number(parsed_number):
            return None  # Invalid phone number

        # Normalize the phone number to international format
        normalized_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        return normalized_number.replace(" ", "")
    except phonenumbers.phonenumberutil.NumberParseException:
        return None


def validate_row_numbers(row):
    if None in (
        normalize_phone_number(row["primary_number"]),
        normalize_phone_number(row["secondary_number"]),
    ):
        return False
    return True
