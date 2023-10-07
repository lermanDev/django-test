import phonenumbers


def normalize_phone_number(phone_number_str: str):
    try:
        # Remove any non-numeric characters and replace hyphens with spaces
        phone_number_str = "".join(
            char for char in str(phone_number_str) if char.isdigit() or char in "+"
        )

        # Parse the phone number string
        parsed_number = phonenumbers.parse(phone_number_str.replace(" ", ""), None)

        # Check if the number is valid
        if not phonenumbers.is_possible_number(parsed_number):
            return None  # Invalid phone number

        # Normalize the phone number to international format without spaces
        normalized_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )
        return normalized_number
    except phonenumbers.phonenumberutil.NumberParseException:
        return None


def validate_row_numbers(row):
    for k, v in row.items():
        if row[k] is None:
            return False

    if None in (
        normalize_phone_number(row["primary_number"]),
        normalize_phone_number(row["secondary_number"]),
    ):
        return False
    return True
