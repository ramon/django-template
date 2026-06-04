import pytest
from apps.core.domain.value_objects.person_name import PersonName
from apps.core.models.mixins import PersonNameMixin
from django.db import models


class TestPersonNameModel(PersonNameMixin, models.Model):
    """
    Concrete implementation of the PersonNameMixin for testing.
    """
    __test__ = False

    class Meta:
        abstract = False  # Allow model to be non-abstract for testing


@pytest.fixture
def person_name_instance():
    """
    Fixture to provide an instance of TestPersonNameModel.
    """
    return TestPersonNameModel(first_name="John", last_name="Doe")


def test_cached_name_property(person_name_instance):
    """
    Test that the cached name property correctly computes the full name.
    """
    expected_full_name = PersonName(first="John", last="Doe")
    assert person_name_instance._cached_name == expected_full_name


def test_name_getter(person_name_instance):
    """
    Test that the name getter returns the full name.
    """
    expected_full_name = PersonName(first="John", last="Doe")
    assert person_name_instance.name == expected_full_name


def test_name_setter(person_name_instance):
    """
    Test that the name setter splits and sets the first and last names correctly.
    """
    person_name_instance.name = "Jane Smith"
    assert person_name_instance.first_name == "Jane"
    assert person_name_instance.last_name == "Smith"
    assert person_name_instance.name == PersonName(first="Jane", last="Smith")


def test_invalid_name_setter(person_name_instance):
    """
    Test that the name setter raises an exception when given an invalid name format.
    """
    with pytest.raises(ValueError):
        person_name_instance.name = "InvalidName"
