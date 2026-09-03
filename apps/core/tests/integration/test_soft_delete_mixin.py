"""SoftDeleteModel is abstract with no concrete model in the project yet, so it needs
a throwaway table -- exercised end to end against the database, unlike the other
mixin unit tests in tests/unit/models/, which never touch a table."""

import pytest
from django.db import connection

from apps.core.models.mixins import SoftDeleteModel
from apps.core.models.mixins.soft_delete import SoftDeleteQuerySet

pytestmark = pytest.mark.django_db


class _SoftDeleteTestModel(SoftDeleteModel):
    """Concrete model for exercising the SoftDeleteModel mixin."""

    __test__ = False

    class Meta:
        app_label = "core"


@pytest.fixture
def model():
    """Creates the table for `_SoftDeleteTestModel` and drops it afterwards."""
    with connection.schema_editor() as editor:
        editor.create_model(_SoftDeleteTestModel)
    yield _SoftDeleteTestModel
    with connection.schema_editor() as editor:
        editor.delete_model(_SoftDeleteTestModel)


def test_is_deleted_reflects_deleted_at(model: type[_SoftDeleteTestModel]) -> None:
    obj = model.objects.create()

    assert obj.is_deleted is False

    obj.delete()

    assert obj.is_deleted is True


def test_delete_sets_deleted_at_instead_of_removing_the_row(
    model: type[_SoftDeleteTestModel],
) -> None:
    obj = model.objects.create()

    obj.delete()

    assert not model.objects.filter(pk=obj.pk).exists()
    assert model.all_objects.get(pk=obj.pk).deleted_at is not None


def test_restore_clears_deleted_at(model: type[_SoftDeleteTestModel]) -> None:
    obj = model.objects.create()
    obj.delete()

    obj.restore()

    assert model.objects.filter(pk=obj.pk).exists()
    assert obj.is_deleted is False


def test_hard_delete_removes_the_row(model: type[_SoftDeleteTestModel]) -> None:
    obj = model.objects.create()

    obj.hard_delete()

    assert not model.all_objects.filter(pk=obj.pk).exists()


def test_queryset_bulk_delete_sets_deleted_at_without_removing_rows(
    model: type[_SoftDeleteTestModel],
) -> None:
    obj = model.objects.create()

    model.objects.filter(pk=obj.pk).delete()

    assert model.all_objects.get(pk=obj.pk).deleted_at is not None


def test_queryset_hard_delete_removes_rows(model: type[_SoftDeleteTestModel]) -> None:
    obj = model.objects.create()

    # `all_objects` is a bare `Manager`, so its queryset isn't a `SoftDeleteQuerySet`
    # (no `.hard_delete()`/`.dead()`) -- and `objects` pre-filters to alive rows,
    # which would make `.dead()` always empty. Built directly, unfiltered.
    SoftDeleteQuerySet(model, using="default").filter(pk=obj.pk).hard_delete()

    assert not model.all_objects.filter(pk=obj.pk).exists()


def test_dead_returns_only_soft_deleted_rows(model: type[_SoftDeleteTestModel]) -> None:
    alive_obj = model.objects.create()
    dead_obj = model.objects.create()
    dead_obj.delete()

    dead = SoftDeleteQuerySet(model, using="default").dead()

    assert list(dead) == [dead_obj]
    assert alive_obj not in dead
