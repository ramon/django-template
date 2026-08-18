"""BasePresenter: envolve um objeto e delega o que nao souber responder."""

from dataclasses import dataclass

import pytest

from apps.core.presenters import BasePresenter


@dataclass
class Produto:
    nome: str
    preco: int


class ProdutoPresenter(BasePresenter[Produto]):
    @property
    def preco_formatado(self) -> str:
        return f"R$ {self.obj.preco / 100:.2f}"


def test_delega_atributos_desconhecidos_ao_objeto() -> None:
    presenter = ProdutoPresenter(Produto(nome="Caneta", preco=350))

    assert presenter.nome == "Caneta"
    assert presenter.preco == 350


def test_expoe_os_atributos_proprios() -> None:
    presenter = ProdutoPresenter(Produto(nome="Caneta", preco=350))

    assert presenter.preco_formatado == "R$ 3.50"


def test_atributo_inexistente_continua_sendo_erro() -> None:
    presenter = ProdutoPresenter(Produto(nome="Caneta", preco=350))

    with pytest.raises(AttributeError):
        _ = presenter.inexistente


def test_collection_envolve_cada_item() -> None:
    produtos = [Produto(nome="Caneta", preco=350), Produto(nome="Papel", preco=1200)]

    presenters = ProdutoPresenter.collection(produtos)

    assert [p.preco_formatado for p in presenters] == ["R$ 3.50", "R$ 12.00"]
    assert all(isinstance(p, ProdutoPresenter) for p in presenters)
