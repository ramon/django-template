# Padrões: testes

## Onde o teste mora

| O que testa | Onde | Precisa de banco? |
| --- | --- | --- |
| regra pura, value object, presenter | `apps/<app>/tests/unit/` | não |
| model, API, view, task com efeito | `apps/<app>/tests/integration/` | sim |
| comportamento que atravessa o projeto (i18n, storage) | `tests/` na raiz | depende |
| fluxo no browser | `tests/e2e/` | sim, e build do frontend |

O espelhamento é intencional: `apps/core/tests/unit/domain/test_phone_number.py` testa
`apps/core/domain/value_objects/phone_number.py`. Quem procura o teste de um arquivo acha
pelo caminho.

Um teste de unidade não deve pedir `django_db`. Se pediu, ou o teste é de integração ou a
regra está na camada errada — ver [`backend.md`](backend.md).

## Fixtures e factories

O `conftest.py` da raiz expõe, para qualquer teste:

- `user` — usuário comum, já com `Profile`;
- `superuser`;
- `auth_client` — test client autenticado como `user`.

As factories ficam em `apps/<app>/tests/factories.py`. `UserFactory` passa pelo
`create_user` do manager, não pelo `objects.create` do factory_boy: só ele faz o hash da
senha e cria o `Profile` associado. Factory nova segue a mesma regra — se o model tem
manager com lógica, a factory usa o manager.

Fixture que importa model mora **dentro** da função: o `conftest.py` da raiz é carregado
antes do Django estar configurado.

## Rodar

```bash
uv run pytest                                   # config.settings.test, sem e2e
uv run pytest --cov=apps --cov-report=term-missing
uv run pytest apps/accounts -k profile
uv run pytest -m e2e                            # só os ponta a ponta
```

Com a stack em containers, o mesmo sem `uv run` — os binários estão no PATH da imagem:
`docker compose exec app pytest`. Os e2e são a exceção: exigem o Chromium do Playwright,
que a imagem de dev não traz, então rodam na máquina.

`addopts` traz `--reuse-db` (banco entre execuções), `--strict-markers` e
`--strict-config` — marker novo tem de ser declarado no `pyproject.toml`, senão a suíte
falha.

## Testes ponta a ponta

Rodam num Chromium real, via `pytest-playwright` e a fixture `live_server`. Ficam fora da
execução padrão porque são lentos e exigem browser:

```bash
uv run playwright install chromium   # uma vez
bun run build                        # fora de DEBUG os templates leem o manifest
uv run pytest -m e2e
uv run pytest -m e2e --headed --slowmo 500
```

Estar em `tests/e2e/` basta: um hook no `conftest.py` do pacote marca todo teste com `e2e`
e `django_db`. Sem build do frontend a suíte é **pulada** com a mensagem do que rodar, em
vez de falhar com arquivo não encontrado.

**Prefira seletores por `name`, `id` ou papel ARIA a texto visível.** A interface é
traduzida (`LANGUAGE_CODE = pt-BR`) e texto quebra o teste na próxima mudança de idioma.

## Frontend

```bash
bun run test            # vitest run
bun run test:watch
bun run test:coverage   # v8
```

Teste ao lado do código, em `*.test.js`, com `happy-dom`. Módulo em `frontend/lib/` é
testado direto; controller Stimulus é testado montando o DOM mínimo que ele espera.

## O que vale a pena testar

- Regra de negócio e valor validado: sempre, e nos casos de borda (é onde o bug mora).
- Contrato de API: status, forma da resposta, e o caso não autorizado.
- Comportamento que já quebrou uma vez: teste de regressão junto do fix, no mesmo commit.
- Convenção verificável por ferramenta: como o BEM em `frontend/styles/bem.test.js` e a
  precedência de tradução em `tests/test_i18n.py`.

E o que não: getter trivial, configuração do Django, e **strings traduzidas** — o
`makemessages` ignora `tests/` justamente para que um teste não injete texto de teste no
catálogo. Afirme sobre a chave ou o comportamento, não sobre a tradução.
