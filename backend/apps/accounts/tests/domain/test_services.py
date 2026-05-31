from datetime import date, datetime

import pytest
from backend.apps.accounts.domain.services import calculate_age


@pytest.mark.parametrize(
    "birth_date, expected_age",
    [
        (date(2000, 1, 1), date.today().year - 2000 - (date.today() < date(date.today().year, 1, 1))),
        (date(1990, 12, 15), date.today().year - 1990 - (date.today() < date(date.today().year, 12, 15))),
        (date.today(), 0),  # Birthday is today
    ],
)
def test_calculate_age_date(birth_date, expected_age):
    """
    Test calculate_age with date objects.
    """
    assert calculate_age(birth_date) == expected_age


@pytest.mark.parametrize(
    "birth_date, expected_age",
    [
        (datetime(2000, 1, 1), date.today().year - 2000 - (date.today() < date(date.today().year, 1, 1))),
        (datetime(1990, 12, 15), date.today().year - 1990 - (date.today() < date(date.today().year, 12, 15))),
        (datetime.combine(date.today(), datetime.min.time()), 0),  # Birthday is today
    ],
)
def test_calculate_age_datetime(birth_date, expected_age):
    """
    Test calculate_age with datetime objects.
    """
    assert calculate_age(birth_date) == expected_age


def test_calculate_age_invalid_input():
    """
    Test calculate_age with invalid input.
    """
    with pytest.raises(AttributeError):
        calculate_age("invalid_date")
