import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models.mixins import DocumentMixin


class TestDocumentModel(DocumentMixin, models.Model):
    """Concrete model for testing the DocumentMixin."""

    __test__ = False

    class Meta:
        app_label = "accounts"


@pytest.fixture
def test_model_instance():
    return TestDocumentModel()


def test_clean_is_a_noop_without_nationality(test_model_instance):
    test_model_instance.clean()

    assert test_model_instance.document is None
    assert test_model_instance.document_type == ""


def test_clean_requires_a_document_once_nationality_is_set(test_model_instance):
    test_model_instance.nationality = "BR"

    with pytest.raises(ValidationError):
        test_model_instance.clean()


def test_clean_rejects_an_invalid_document_for_the_nationality(test_model_instance):
    test_model_instance.nationality = "BR"
    test_model_instance.document = "123.456.789-00"

    with pytest.raises(ValidationError):
        test_model_instance.clean()


def test_clean_normalizes_document_and_derives_type_for_brazil(test_model_instance):
    test_model_instance.nationality = "BR"
    test_model_instance.document = "529.982.247-25"

    test_model_instance.clean()

    assert test_model_instance.document == "52998224725"
    assert test_model_instance.document_type == "cpf"


def test_clean_normalizes_document_and_derives_type_for_the_us(test_model_instance):
    test_model_instance.nationality = "US"
    test_model_instance.document = "123-45-6789"

    test_model_instance.clean()

    assert test_model_instance.document == "123456789"
    assert test_model_instance.document_type == "ssn"


def test_clean_falls_back_to_passport_for_an_unsupported_nationality(test_model_instance):
    test_model_instance.nationality = "FR"
    test_model_instance.document = "ab 12-cd 34"

    test_model_instance.clean()

    assert test_model_instance.document == "AB12CD34"
    assert test_model_instance.document_type == "passport"
