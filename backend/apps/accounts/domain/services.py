from datetime import datetime, date


def calculate_age(birth_date: datetime | date) -> int:
    """
    Calculate age in years based on the provided birth date.

    Args:
        birth_date: The birth date as a datetime or date object.

    Returns:
        The age in years as an integer.
    """
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()

    today = date.today()
    age = today.year - birth_date.year

    # Adjust age if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age
