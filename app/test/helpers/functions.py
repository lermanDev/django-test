import phonenumbers


def normalize_phone_number(phone_number_str: str):
    try:
        print(phone_number_str)
        # Remove any non-numeric characters and replace hyphens with spaces
        phone_number_str = "".join(
            char for char in phone_number_str if char.isdigit() or char in "+"
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
        print("NONE ERROR", phone_number_str)
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


# File XLSX Validation
def is_valid_filetype(data, valid_content_types):
    import magic

    content_type = magic.from_buffer(data.read(), mime=True)
    data.seek(0)

    if content_type not in valid_content_types:
        return {"result": False, "extra": content_type}

    return {"result": True, "extra": content_type}
