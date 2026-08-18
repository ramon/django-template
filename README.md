# Django Project Template

Template de projeto Django com foco em organização por domínio, tipagem forte, frontend
server-rendered moderno e separação clara entre configuração do framework e configuração
da aplicação.

## Visão geral

O projeto vive na raiz do repositório: `manage.py`, `apps/` e `config/` no mesmo nível,
sem uma pasta `backend/` intermediária.

O Django é responsável pela renderização HTML e pela API; o Vite atua apenas como pipeline
de assets, seguindo o modelo oficial de *backend integration* — dev server em
desenvolvimento e `manifest.json` em produção.

## Stack principal

### Backend

- Django 6.x.
- Django Ninja para APIs HTTP tipadas, com renderer `orjson`.
- `django-allauth` (com `mfa` e `socialaccount`) para autenticação.
- `django-environ` para settings do framework: `DEBUG`, `SECRET_KEY`, `DATABASE_URL`, cache.
- `pydantic-settings` para configuração da aplicação e de integrações.
- Celery + Redis/Valkey para tarefas assíncronas.
- `structlog` + `django-guid` para logs estruturados com correlation id.
- Sentry e (opcionalmente) Prometheus para observabilidade.
- PostgreSQL via `psycopg`.
- pytest para testes de unidade e `pytest-playwright` para ponta a ponta.
- Ruff + MyPy + `django-stubs` para lint e tipagem.

### Frontend

- Tailwind CSS 4 para estilização.
- HTMX para requests parciais e troca de fragmentos HTML vindos do servidor.
- Stimulus para comportamento cliente estruturado e reutilizável.
- Alpine.js para microestado local, quando um controller Stimulus seria demais.
- Vite para bundling e dev server.
- Bun para instalar dependências e executar o pipeline frontend.
- Biome para lint e formatação de JS/CSS; Stylelint para a convenção BEM.
- Vitest + happy-dom para testes.

## Estrutura do projeto

```text
.
├── manage.py
├── config/
│   ├── asgi.py / wsgi.py / celery.py
│   ├── settings/
│   │   ├── base.py             # importa os parts, em ordem semântica
│   │   ├── development.py
│   │   ├── test.py
│   │   ├── production.py
│   │   └── parts/              # um módulo por assunto (django, cache, logging, ...)
│   ├── app_settings/           # pydantic-settings: app, features, integrações
│   └── urls/                   # root, admin, web, api
├── apps/
│   ├── core/                   # utilidades transversais, templatetags, value objects
│   └── accounts/               # usuários, perfis, API de perfil
├── frontend/
│   ├── entries/                # entrypoints do Vite
│   ├── styles/
│   ├── lib/                    # módulos utilitários (ex.: CSRF do HTMX)
│   └── controllers/            # controllers Stimulus, auto-registrados
├── templates/
│   ├── layouts/                # base.html
│   ├── pages/                  # páginas (a home de exemplo mora aqui)
│   └── components/             # componentes django-cotton
├── static/                     # STATICFILES_DIRS; recebe dist/ do build do Vite
├── public/                     # SERVESTATIC_ROOT: static/, media/, manifest.json, favicon.svg
├── tests/
│   └── e2e/                    # testes ponta a ponta (Playwright)
├── locale/
├── tools/                      # arquivos de apoio (ex.: prometheus.yml)
├── .github/workflows/          # CI
├── conftest.py                 # fixtures compartilhadas por toda a suite
├── .env.example
├── pyproject.toml / uv.lock
├── package.json / bun.lock
├── vite.config.mjs
└── docker-compose.yml
```

## Convenções arquiteturais

- `config/settings/parts/`: cada arquivo cobre um assunto (django, security, cache, logging,
  celery, sentry, observability…). **A ordem dos imports em `base.py` é semântica** — os parts
  mutam `INSTALLED_APPS` e `MIDDLEWARE` em sequência, por isso o arquivo é marcado com
  `# ruff: noqa: I001` para o isort não reordenar.
- `config/app_settings/`: configuração da aplicação tipada com Pydantic, em três recortes —
  `AppSettings` (prefixo `APP_`), `FeatureSettings` (`FEATURE_`) e `IntegrationSettings`
  (`INTEGRATION_`).
- `apps/<domínio>/`: modelos, domínio, serviços, API e testes de cada contexto.
- `apps/core/`: utilidades globais — mixins de modelo, value objects, templatetags.
- `templates/components/`: componentes `django-cotton` (`COTTON_DIR = "components"`).

## Settings

Settings do framework ficam em `config/settings/` e são lidos com `django-environ`.
Configuração de aplicação e de integrações fica em `config/app_settings/`, com
`pydantic-settings`, e é consumida diretamente pelo código:

```python
from config.app_settings import get_app_settings, get_integration_settings

region = get_app_settings().phone_number_region     # APP_PHONE_NUMBER_REGION
dsn = get_integration_settings().SENTRY_DSN         # INTEGRATION_SENTRY_DSN
```

Módulos de settings disponíveis: `config.settings.development` (padrão do `manage.py`),
`config.settings.test` (usado pelo pytest) e `config.settings.production`.

## Frontend: Vite + Bun

O build sai em `static/dist/`, que está dentro de `STATICFILES_DIRS` — assim o
`collectstatic` leva os assets para `public/static/` e o `{% static %}` resolve as URLs com
hash.

As template tags ficam em `apps/core/templatetags/vite.py` e expõem `{% vite_css %}`,
`{% vite_js %}` e `{% vite_asset %}`. **O argumento é a chave do manifest**, que o Vite gera
a partir do caminho do input relativo à raiz do projeto — a mesma string que o dev server
usa, evitando um mapeamento paralelo entre dev e produção:

```django
{% load vite %}
{% vite_css 'frontend/entries/app.js' %}
{% vite_js 'frontend/entries/app.js' %}
```

Para adicionar um entrypoint, registre-o em `vite.config.mjs` (`build.rollupOptions.input`)
e referencie o caminho do arquivo no template.

## Comportamento no cliente

A divisão de responsabilidades é intencional:

| Biblioteca | Quando usar |
|---|---|
| HTMX | buscar ou trocar fragmentos HTML renderizados pelo servidor |
| Stimulus | comportamento estruturado e reutilizável, ligado a um pedaço de DOM |
| Alpine.js | microestado local — um dropdown, um toggle — sem criar um controller |

Tudo é inicializado em `frontend/entries/app.js`.

**Stimulus** registra sozinho qualquer `frontend/controllers/*_controller.js`; o nome vem do
arquivo, então `hello_controller.js` responde a `data-controller="hello"`:

```html
<div data-controller="hello">
  <input data-hello-target="name" type="text">
  <button data-action="hello#greet">Cumprimentar</button>
  <span data-hello-target="output"></span>
</div>
```

**HTMX** já envia o CSRF token em toda request unsafe: um listener de `htmx:configRequest`
copia o valor de `<meta name="csrf-token">` para o header `X-CSRFToken`, sem o qual o Django
rejeitaria o POST.

**Alpine** é reinicializado nos fragmentos que o HTMX injeta, via
`htmx.onLoad(content => Alpine.initTree(content))` — sem isso, HTML trocado pelo HTMX viria
com os `x-data` inertes. O Stimulus não precisa disso: ele observa o DOM sozinho.

`window.htmx` e `window.Alpine` ficam expostos para uso em atributos inline dos templates.

## Instalação

### Requisitos

- Python 3.14+
- Bun
- PostgreSQL e Redis/Valkey (o `docker-compose.yml` sobe ambos)

Com [mise](https://mise.jdx.dev) instalado, `mise install` provê Python, uv, Bun e Ruff nas
versões do `mise.toml`.

### Dependências

```bash
uv sync          # backend
bun install      # frontend
```

### Serviços locais

```bash
docker compose up -d database kv-database
```

## Ambiente local

`.env.example` documenta todas as variáveis lidas pelo projeto, com os valores que
casam com o `docker-compose.yml`:

```bash
cp .env.example .env
```

`SECRET_KEY` é a única sem default — o boot falha sem ela. Gere uma com:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Variáveis do framework não têm prefixo. As da aplicação seguem o prefixo do modelo
correspondente em `app_settings` — por exemplo `INTEGRATION_SENTRY_DSN` para o DSN do Sentry.

## Executando o projeto

```bash
python manage.py migrate
python manage.py runserver     # usa config.settings.development
bun run dev                    # Vite com HMR na porta 8001
```

O Django serve HTML e endpoints; o Vite serve os assets com HMR.

`http://localhost:8000/` responde com uma página de exemplo — "Seu app está no ar" —
que exercita o layout `django-cotton`, os assets do Vite e os três frameworks de
cliente (HTMX, Stimulus e Alpine). Com `DEBUG=True` ela ainda lista a configuração
que está de fato em uso (banco, cache, idioma, estado do build). Ela vive em
`apps/core/views.py` e `templates/pages/home.html`; apague os dois quando o projeto
tiver conteúdo próprio.

## Build de produção

```bash
bun run build
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --noinput
```

O Vite gera os assets e o `manifest.json` em `static/dist/`; o `collectstatic` publica em
`public/static/`, de onde o ServeStatic os entrega.

## Observabilidade

- **Health check**: `GET /health/` verifica cache e banco. Aceita `?format=json`, `text`,
  `openmetrics`. Retorna 500 se algum check falhar.
- **Logs**: `structlog` em JSON, com correlation id injetado pelo `django-guid` e exposto no
  header `X-Correlation-Id`.
- **Sentry**: ativado fora de `DEBUG` quando `INTEGRATION_SENTRY_DSN` está definido.
- **Prometheus**: com `ENABLE_PROMETHEUS=true`, as métricas ficam em `/monitoring/metrics`.
  `docker compose up -d prometheus` sobe um Prometheus já configurado em
  `tools/prometheus.yml` para raspar a aplicação rodando no host.

## Testes e qualidade

```bash
pytest                                  # usa config.settings.test
pytest --cov=apps --cov-report=term-missing

ruff check . --fix
ruff format .
mypy apps tests
```

### Frontend

Biome cobre lint e formatação de JS e CSS num binário só, como o Ruff faz no Python; os
testes rodam em Vitest com `happy-dom`, ao lado do código em `*.test.js`:

```bash
bun run lint          # biome + stylelint
bun run lint:js       # só biome
bun run lint:css      # só a convenção BEM
bun run lint:fix      # corrige o que é automatizável nos dois
bun run format        # só formatação
bun run test          # vitest run
bun run test:watch    # vitest em watch
bun run test:coverage # cobertura v8
```

#### Convenção BEM no CSS

Classes CSS seguem BEM, validado pelo Stylelint (`.stylelintrc.json`):

```
bloco[__elemento][--modificador]     tudo em kebab-case

.card                 .card__title              .card--featured
.user-profile         .user-profile__avatar     .card__title--muted
```

Rejeita `PascalCase`, `camelCase`, `_underscore` simples, elemento aninhado
(`.card__title__deep`) e modificador duplicado. A convenção é coberta por testes em
`frontend/styles/bem.test.js`, que rodam contra o `.stylelintrc.json` real — mudar a regra
sem atualizar o teste quebra o CI.

Formatação e nomenclatura ficam em ferramentas distintas de propósito: um formatter reescreve
espaçamento e não tem como julgar nomes; o Biome cuida do formato, o Stylelint da convenção.
Como o Tailwind é utility-first, a regra vale para o CSS próprio do projeto — as utilitárias
aplicadas no HTML não passam por aqui.

O pre-commit roda o Biome nos arquivos JS/CSS/JSON alterados, junto do Ruff nos Python.

Lógica de comportamento fica em `frontend/lib/`, não solta no entrypoint — `app.js` só
orquestra, e o que tem regra (como o header CSRF do HTMX) vira módulo testável.

### Testes ponta a ponta

Os e2e vivem em `tests/e2e/` e rodam num Chromium real, via `pytest-playwright` e a
fixture `live_server` do pytest-django. Como são lentos e exigem browser, ficam **fora da
execução padrão** (`addopts` traz `-m "not e2e"`):

```bash
uv run playwright install chromium   # uma vez
bun run build                        # os templates leem o manifest do Vite fora de DEBUG
pytest -m e2e                        # só os e2e
pytest -m e2e --headed --slowmo 500  # acompanhando no browser
```

Estar em `tests/e2e/` já basta: um hook no `conftest.py` marca todo teste do pacote com
`e2e` e `django_db`. Se o build do frontend não existir, a suíte é pulada com uma mensagem
dizendo o que rodar, em vez de falhar com erro de arquivo não encontrado.

Prefira seletores por `name`, `id` ou papel ARIA a texto visível — a interface é traduzida
(`LANGUAGE_CODE = pt-BR`) e textos quebram os testes a cada mudança de idioma.

Instale os hooks de pre-commit uma vez com `pre-commit install`; eles rodam `ruff check --fix`
e `ruff format` a cada commit.

O MyPy roda em modo `strict` e o código está limpo — o CI falha se um erro de tipagem for
introduzido. Alguns pontos são silenciados por configuração no `pyproject.toml`, cada um com
o motivo ao lado: `prop-decorator` (o mypy não suporta `@computed_field` sobre `@property`,
o padrão do Pydantic v2), generics em `apps/*/admin.py` (`ModelAdmin` é genérico para o
django-stubs mas não define `__class_getitem__`, então parametrizá-lo quebra em runtime) e
`ignore_missing_imports` para dependências sem stubs.

## CI

`.github/workflows/ci.yml` roda em push para `master` e em pull requests:

| Job | O que valida |
|-----|--------------|
| `lint` | `ruff check` e `ruff format --check` |
| `test` | `manage.py check` nos três cenários, migrations em dia e `pytest` com cobertura, contra Postgres e Valkey |
| `frontend` | Biome, Stylelint (BEM), Vitest, `vite build` e a presença do manifest |
| `e2e` | `pytest -m e2e` num Chromium real, com build do frontend; anexa `test-results/` se falhar |
| `typecheck` | `mypy apps tests` em modo strict |

## Notas finais

Este template foi pensado para favorecer:

- separação clara entre configuração do framework e configuração da aplicação.
- organização por contexto/domínio.
- uso de HTML server-rendered com frontend progressivamente enriquecido.
- uma base sustentável para crescer sem depender de SPA por padrão.
