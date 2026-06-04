# apps/core/tests/test_person_name.py

import pytest
from apps.core.domain.value_objects.person_name import PersonName


def test_from_full_name():
    """Tests creating a PersonName instance from a full name."""
    full_name = "John Doe"
    person_name = PersonName.from_full_name(full_name)
    assert person_name.first == "John"
    assert person_name.last == "Doe"


def test_full_property():
    """Tests the full property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.full == "John Doe"


def test_familiar_property():
    """Tests the familiar property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.familiar == "John D."


def test_abbreviated_property():
    """Tests the abbreviated property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.abbreviated == "J. Doe"


def test_sorted_property():
    """Tests the sorted property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.sorted == "Doe, John"


def test_initials_property():
    """Tests the initials property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.initials == "JD"


def test_mentionable_property():
    """Tests the mentionable property of PersonName."""
    person_name = PersonName(first="John", last="Doe")
    assert person_name.mentionable == "johnd"


def test_possessive_with_full():
    """Tests the possessive method with the full name."""
    person_name = PersonName(first="Chris", last="James")
    assert person_name.possessive("full") == "Chris James'"


def test_possessive_with_first():
    """Tests the possessive method with the first name."""
    person_name = PersonName(first="Chris", last="James")
    assert person_name.possessive("first") == "Chris'"


def test_possessive_with_last():
    """Tests the possessive method with the last name."""
    person_name = PersonName(first="Chris", last="James")
    assert person_name.possessive("last") == "James'"
