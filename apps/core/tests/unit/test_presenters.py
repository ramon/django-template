"""BasePresenter: wraps an object and delegates what it doesn't know how to answer."""

from dataclasses import dataclass

import pytest

from apps.core.presenters import BasePresenter


@dataclass
class Product:
    name: str
    price: int


class ProductPresenter(BasePresenter[Product]):
    @property
    def formatted_price(self) -> str:
        return f"R$ {self.obj.price / 100:.2f}"


def test_delegates_unknown_attributes_to_the_object() -> None:
    presenter = ProductPresenter(Product(name="Pen", price=350))

    assert presenter.name == "Pen"
    assert presenter.price == 350


def test_exposes_its_own_attributes() -> None:
    presenter = ProductPresenter(Product(name="Pen", price=350))

    assert presenter.formatted_price == "R$ 3.50"


def test_missing_attribute_still_raises() -> None:
    presenter = ProductPresenter(Product(name="Pen", price=350))

    with pytest.raises(AttributeError):
        _ = presenter.missing


def test_collection_wraps_each_item() -> None:
    products = [Product(name="Pen", price=350), Product(name="Paper", price=1200)]

    presenters = ProductPresenter.collection(products)

    assert [p.formatted_price for p in presenters] == ["R$ 3.50", "R$ 12.00"]
    assert all(isinstance(p, ProductPresenter) for p in presenters)
