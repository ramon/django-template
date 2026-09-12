# Padrões: testes

## Onde o teste mora

| O que testa | Onde | Precisa de banco? |
| --- | --- | --- |
| regra pura, value object, presenter | `apps/<app>/tests/unit/` | não |
| model, API, view, task com efeito | `apps/<app>/tests/integration/` | sim |
| comportamento que atravessa o projeto (i18n, storage) | `tests/` na raiz | depende |
| fluxo no browser preso a um app | `apps/<app>/tests/e2e/` | sim, e build do frontend |
| fluxo no browser que cruza mais de um app | `tests/e2e/` na raiz | sim, e build do frontend |

O espelhamento é intencional: `apps/core/tests/unit/domain/test_phone_number.py` testa
`apps/core/domain/value_objects/phone_number.py`. Quem procura o teste de um arquivo acha
pelo caminho.

Um teste de unidade não deve pedir `django_db`. Se pediu, ou o teste é de integração ou a
regra está na camada errada — ver [`backend.md`](backend.md).

Nome de função de teste é código: em inglês, descrevendo o comportamento, sem exceção —
ver [`AGENTS.md#estilo`](../../AGENTS.md#estilo).

## Fixtures e factories

O `conftest.py` da raiz expõe, para qualquer teste:

- `user` — usuário comum, já com `Profile`;
- `superuser`;
- `auth_client` — test client autenticado como `user`;
- `e2e_page` — `Page` do Playwright já apontando para o `live_server`;
- `verified_user` — usuário com e-mail verificado no allauth (passa no login);
- `login` — helper `login(page, live_server, user)` que autentica pelo formulário real.

Os três últimos são de e2e mas ficam globais de propósito: servem tanto a `tests/e2e/`
quanto a `apps/<app>/tests/e2e/`. São instanciados só quando um teste os pede.

As factories ficam em `apps/<app>/tests/factories.py`. `UserFactory` passa pelo
`create_user` do manager, não pelo `objects.create` do factory_boy: só ele faz o hash da
senha e cria o `Profile` associado. Factory nova segue a mesma regra — se o model tem
manager com lógica, a factory usa o manager.

Fixture que importa model mora **dentro** da função: o `conftest.py` da raiz é carregado
antes do Django estar configurado.

## Rodar

```bash
uv run pytest                                   # = make test; config.settings.test, sem e2e
uv run pytest --cov=apps --cov-branch --cov-report=term-missing   # = make test-cov-py
uv run pytest apps/accounts -k profile
uv run pytest -m e2e                            # = make e2e (que builda antes)
```

Os alvos do `Makefile` são atalhos para exatamente esses comandos — `make test-cov` roda
os dois lados (`test-cov-py` + `test-cov-js`), e `make check` encadeia `lint typecheck
test-cov`. Para variar (um path, `-k`, um marker), use o comando cru: é o que o CI roda.
Um caso em que o alvo é melhor que o comando cru é o e2e — `make e2e` garante o `bun run
build` antes, cuja falta faz o teste ser pulado em vez de falhar.

Com a stack em containers, o mesmo sem `uv run` — os binários estão no PATH da imagem:
`docker compose exec app pytest`. Os e2e são a exceção: exigem os browsers do Playwright,
que a imagem de dev não traz, então rodam na máquina.

`addopts` traz `--reuse-db` (banco entre execuções), `--strict-markers` e
`--strict-config` — marker novo tem de ser declarado no `pyproject.toml`, senão a suíte
falha. Traz também `--browser chromium --browser webkit`: os e2e rodam nos dois motores, o
resto da suíte não pede a fixture `page` e ignora as flags.

### Cobertura de Python

```bash
uv run pytest --cov=apps --cov-branch --cov-report=term-missing   # = make test-cov-py
```

Piso de 90% de linhas e 85% de branches, avaliados em separado sobre o total agregado de
`apps/` — não arquivo a arquivo, o mesmo espírito do `coverage.thresholds` do
`vitest.config.mjs` (ver [Cobertura de JS](#cobertura-de-js)).

`--cov-fail-under` do pytest-cov não serve aqui: ele compara um número só, que o
coverage.py calcula como média ponderada de linha e branch juntos — dá pra passar com
85% combinado tendo branch coverage bem abaixo disso. Por isso o piso é um hook
`pytest_sessionfinish` no `conftest.py` da raiz: ele só age quando a sessão rodou com
`--cov` (então `uv run pytest` sozinho não afere nada), lê o mesmo `Coverage` que o
`--cov` já populou e falha a sessão se `percent_statements_covered` ou
`percent_branches_covered` caírem abaixo do piso.

## Testes ponta a ponta

Rodam em browser real via `pytest-playwright` e a fixture `live_server`. Ficam fora da
execução padrão porque são lentos e exigem browser.

```bash
uv run playwright install chromium webkit   # uma vez — webkit é o motor do Safari
bun run build                               # fora de DEBUG os templates leem o manifest
uv run pytest -m e2e
uv run pytest -m e2e --browser webkit --headed --slowmo 500
```

**Dois motores, sempre.** Cada e2e roda em Chromium e em WebKit (o motor do Safari) — é o
que `addopts` fixa e o que o CI instala. Um caso que só faz sentido num motor recebe
`@pytest.mark.skip_browser("...")` ou `@pytest.mark.only_browser("...")`, com o porquê.

**Onde o teste mora.** `tests/e2e/` na raiz é só para fluxo que atravessa mais de um app,
ou para o que não é de nenhum app (o shell do projeto: layout, tema, login do admin). E2e
preso a um app — renderização de um formulário, o fluxo de cadastro, o health check — vai
para `apps/<app>/tests/e2e/`, espelhando o resto da suíte do app. Estar em qualquer
`tests/e2e/` basta: um hook no `conftest.py` da raiz marca o teste com `e2e` e `django_db`,
e checa o build. Fixtures de e2e comuns (`e2e_page`, `verified_user`, `login`) são globais,
no `conftest.py` da raiz; o que só um app usa fica no `conftest.py` do `tests/` desse app.

Sem build do frontend o teste é **pulado** com a mensagem do que rodar, em vez de falhar
com arquivo não encontrado.

**Prefira seletores por `name`, `id` ou papel ARIA a texto visível.** A interface é
traduzida (`LANGUAGE_CODE = pt-BR`) e texto quebra o teste na próxima mudança de idioma.

## Frontend

```bash
bun run test            # vitest run
bun run test:watch
bun run test:coverage   # = make test-cov-js; v8, com o piso do vitest.config.mjs
```

Teste ao lado do código, em `*.test.js`, com `happy-dom`. Módulo em `frontend/lib/` é
testado direto; controller Stimulus é testado montando o DOM mínimo que ele espera.

### Cobertura de JS

`vitest.config.mjs` define `coverage.thresholds` em 90% (linhas, statements, funções e
branches) sobre `frontend/**/*.js`. `bun run test:coverage` falha se cair abaixo — é o
mesmo comando que o job `frontend` do CI roda.

Ficam fora do `include`/`exclude` do relatório os arquivos que só ligam e não decidem:
`frontend/entries/**` e `frontend/controllers/index.js` (o `Application.start()` e o
`import.meta.glob` de registro automático). Regra testável que aparecer nesses arquivos
vira módulo em `frontend/lib/` com teste ao lado — é o mesmo padrão de
`stimulus-identifier.js`, que existe só para tirar a derivação do identificador do
Stimulus (`hello_controller.js` → `hello`) de dentro do loop de `controllers/index.js` e
deixá-la testável.

Se um módulo novo empurrar a cobertura abaixo do piso, o gate é o sinal de que falta
teste — não motivo para abaixar o número. Se o piso virar atrito real em um projeto
gerado a partir do template, ajuste-o em `vitest.config.mjs` e registre o porquê em
[`docs/adr/`](../adr/README.md), como qualquer divergência da base.

## O que vale a pena testar

- Regra de negócio e valor validado: sempre, e nos casos de borda (é onde o bug mora).
- Contrato de API: status, forma da resposta, e o caso não autorizado.
- Comportamento que já quebrou uma vez: teste de regressão junto do fix, no mesmo commit.
- Convenção verificável por ferramenta: como o BEM em `frontend/styles/bem.test.js` e a
  precedência de tradução em `tests/test_i18n.py`.

E o que não: getter trivial, configuração do Django, e **strings traduzidas** — o
`makemessages` ignora `tests/` justamente para que um teste não injete texto de teste no
catálogo. Afirme sobre a chave ou o comportamento, não sobre a tradução.
