import pytest
from apps.core.models.mixins import PhoneNumberMixin
from django.db import models


class TestPhoneNumberModel(PhoneNumberMixin, models.Model):
    """Concrete model for testing the PhoneNumberMixin."""
    __test__ = False

    class Meta:
        app_label = 'core'


@pytest.fixture
def test_model_instance():
    """Fixture for creating a TestModel instance."""
    return TestPhoneNumberModel()


def test_phone_getter(test_model_instance):
    """Test the phone property getter."""
    test_model_instance.phone_number = "+5511987654321"
    assert test_model_instance.phone.e164 == "+5511987654321"


def test_phone_setter(test_model_instance):
    """Test the phone property setter."""
    test_model_instance.phone = "+5511987654321"
    assert test_model_instance.phone_number == "+5511987654321"


def test_phone_setter_invalid_format(test_model_instance):
    """Test setting an invalid phone number raises a ValueError."""
    with pytest.raises(ValueError):
        test_model_instance.phone = "invalid_phone"


def test_phone_property_reflects_change(test_model_instance):
    """Ensure the phone property reflects changes in the phone_number field."""
    test_model_instance.phone_number = "+81312345678"
    assert test_model_instance.phone.national == "03-1234-5678"
