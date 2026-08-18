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
- `django-allauth` (com `mfa` e `socialaccount`) para autenticação — ver
  [`docs/standards/auth.md`](docs/standards/auth.md).
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
│   ├── core/                   # utilidades transversais, templatetags, tasks, value objects
│   └── accounts/               # usuários, perfis, API de perfil, factories
│       └── locale/             # catálogo do app (cada app tem o seu)
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
├── locale/                     # catálogo global (templates/, config/)
├── docs/                       # padrões, ADRs, especificações e planos
│   ├── standards/              # como se escreve código aqui
│   ├── adr/                    # decisões arquiteturais registradas
│   ├── specs/                  # especificações de features
│   └── plans/                  # planos de implementação
├── tools/                      # arquivos de apoio (ex.: prometheus.yml)
├── .github/
│   ├── workflows/              # CI
│   ├── dependabot.yml
│   └── pull_request_template.md
├── conftest.py                 # fixtures compartilhadas por toda a suite
├── AGENTS.md                   # instruções canônicas para agentes
├── CLAUDE.md                   # aponta para AGENTS.md
├── .env.example
├── Dockerfile                  # produção, multi-stage
├── Dockerfile.dev              # desenvolvimento, usada pelo compose
├── Procfile                    # release / web / worker / beat
├── .editorconfig
├── LICENSE                     # MIT
├── pyproject.toml / uv.lock
├── package.json / bun.lock
├── vite.config.mjs
└── docker-compose.yml
```

## Documentação

Este README cobre a stack, a instalação e a execução. O resto da documentação vive em
[`docs/`](docs/), organizada por propósito:

| Pasta | Guarda | Pergunta que responde |
| --- | --- | --- |
| [`docs/standards/`](docs/standards/) | convenções de código, por área | "como se faz isso neste projeto?" |
| [`docs/adr/`](docs/adr/) | decisões arquiteturais registradas | "por que está assim?" |
| [`docs/specs/`](docs/specs/) | especificações de features | "o que exatamente precisa acontecer?" |
| [`docs/plans/`](docs/plans/) | planos de implementação em andamento | "onde este trabalho parou?" |

Agentes de código leem [`AGENTS.md`](AGENTS.md) — o arquivo canônico de instruções, que
aponta para `docs/`. Regra nova para agentes entra lá, não nos arquivos por harness
(`CLAUDE.md`).

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

### Storage de uploads

Por padrão os uploads vão para disco (`public/media/`). Dentro de um container isso
é efêmero — todo deploy perde os arquivos — então qualquer ambiente com upload de
usuário precisa de storage remoto:

```bash
uv sync --extra s3      # boto3 + botocore, 31 MB, fora da instalação padrão
```

e no `.env`, `USE_S3=True` mais `AWS_STORAGE_BUCKET_NAME`. `AWS_S3_ENDPOINT_URL`
atende S3 compatível (MinIO, R2, Spaces). As credenciais seguem a cadeia padrão do
boto3, então em cluster o certo é não definir nenhuma e usar IAM role.

## Traduções

Cada app tem o seu catálogo em `apps/<app>/locale/`. O `locale/` da raiz — o único em
`LOCALE_PATHS` — guarda apenas o que não pertence a app nenhum: `templates/` e `config/`.

Um comando só cuida dos dois:

```bash
python manage.py makemessages          # todos os idiomas de settings.LANGUAGES
python manage.py compilemessages
```

Não é preciso entrar em cada app: o Django decide o destino durante a varredura — ao
encontrar um diretório `locale/`, passa a mandar para lá tudo que estiver abaixo do
diretório pai. Como cada app tem o seu, as strings do app ficam no app.

O `makemessages` deste projeto (`apps/core/management/commands/`) muda três padrões:

- **`--no-location`**: sem o par `arquivo:linha`, que muda a cada refatoração e enche o
  diff de ruído. Para investigar uma string, `--add-location=file` volta atrás.
- **`--no-obsolete`**: mensagens que saíram do código somem, em vez de acumularem
  comentadas com `#~`.
- **sem `POT-Creation-Date`**: o `msgmerge` a reescreve a cada execução, o que faria todo
  `makemessages` sujar os seis catálogos sem mudar tradução nenhuma.

Os três juntos deixam o comando idempotente, e é isso que permite o CI falhar quando
alguém adiciona uma string traduzível sem atualizar o catálogo.

Sem `-l/-x/-a`, os idiomas vêm de `settings.LANGUAGES`. `node_modules`, `static/dist` e
`tests` ficam fora da varredura — um teste que afirme algo sobre uma string traduzida
injetaria essa string no catálogo. Para excluir outros caminhos, use `--ignore=<path>`.

O `compilemessages` nativo do Django não ignora nada por padrão: sem override, ele
recompilaria os `.mo` de todo pacote em `.venv`. O override deste projeto já aplica
`--ignore=.venv --ignore=node_modules`.

### Precedência

Vale a ordem do Django, verificada neste projeto: `LOCALE_PATHS` (o `locale/` da raiz)
ganha de tudo; entre apps, quem vem **antes** em `INSTALLED_APPS` ganha. Na prática,
`django.contrib.auth` sobrepõe uma tradução de mesmo `msgid` em `apps/accounts` — se
precisar cravar um texto, o lugar é o catálogo da raiz.

Os `.po` são versionados; os `.mo`, não (`.gitignore`). A compilação é passo de build —
o `Dockerfile` a executa no estágio `assets`, e o job `test` do CI antes do pytest.

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

Para subir tudo dentro de containers, incluindo a aplicação, veja
[Executando o projeto](#executando-o-projeto).

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

### Com Docker (um comando)

```bash
cp .env.example .env
docker compose up
```

Sobe banco, cache, aplicação (já migrada), worker do Celery, beat e o dev server do
Vite. O código é montado como volume, então o autoreload continua funcionando. O
Prometheus fica atrás de um profile para não entrar no `up` padrão:

```bash
docker compose --profile observability up
```

### Sem Docker

```bash
docker compose up -d database kv-database
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

### Atalhos: `make`

O `Makefile` embrulha os comandos acima e os de [Testes e qualidade](#testes-e-qualidade)
nos dois caminhos — `make up`/`make services` para os containers, o resto (`make lint`,
`make test`, `make migrate` etc.) rodando `uv run`/`bun run` na máquina, e os equivalentes
`make dtest`/`make dlint`/... executando dentro do container `app`. `make help` lista tudo.
Não é obrigatório: os comandos "crus" nesta página continuam válidos e são o que o CI roda.

## Build de produção

```bash
bun run build
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --noinput
```

O Vite gera os assets e o `manifest.json` em `static/dist/`; o `collectstatic` publica em
`public/static/`, de onde o ServeStatic os entrega.

## Imagens Docker

| Arquivo | Uso |
| --- | --- |
| `Dockerfile` | produção, em quatro estágios |
| `Dockerfile.dev` | desenvolvimento, usada pelo `docker-compose.yml` |
| `Procfile` | declaração de processos (`release`, `web`, `worker`, `beat`) |

A imagem de produção separa build de runtime: o bundle do Vite sai de um estágio com
Bun, o `.venv` de um estágio com uv (`--no-dev`) e o `collectstatic` de um estágio que
já tem os dois. O estágio final parte de `python:3.14-slim-bookworm` e recebe apenas o
`.venv`, o código da aplicação, `public/` e o `manifest.json` do Vite — nenhum `uv`,
`bun`, `node_modules`, compilador, teste ou dependência de dev sobrevive. O job
`docker` do CI verifica isso a cada push.

```bash
docker build -t app:prod .
docker run --rm -p 8000:8000 --env-file .env app:prod
```

O processo roda como usuário sem privilégios e traz um `HEALTHCHECK` apontando para
`/health/`. Em produção `SECURE_SSL_REDIRECT` está ligado, então toda requisição em
HTTP puro recebe 301 — o proxy que termina TLS precisa enviar `X-Forwarded-Proto`,
que é o que `SECURE_PROXY_SSL_HEADER` espera. É por isso que o `HEALTHCHECK` manda
esse cabeçalho.

Pré-compilar os `.pyc` custa cerca de 60 MB e economiza a compilação no primeiro
request de cada worker. Para trocar tamanho por latência inicial:

```bash
docker build --build-arg COMPILE_BYTECODE=0 -t app:prod .
```

O extra `s3` também é opcional na imagem, pelo mesmo motivo:

```bash
docker build --build-arg UV_EXTRA=s3 -t app:prod .
```

O `Procfile` também vai dentro da imagem, então plataformas que o leem em deploys por
Dockerfile (Dokku, por exemplo) reconhecem os quatro tipos de processo.

## Sondas de saúde

| Rota | O que verifica | Para quem |
| --- | --- | --- |
| `/health/` | banco, os dois aliases de cache e o storage | balanceador / readiness |
| `/health/workers/` | worker do Celery respondendo ao ping | monitoração |

Estão separadas de propósito: o worker não é dependência do processo web. Derrubar a
aplicação do balanceador porque uma fila caiu troca uma falha parcial por uma total.
DNS e e-mail ficam fora das duas — fazem chamada externa e tornariam a sonda instável.

O check de storage grava, lê e apaga um arquivo a cada requisição. É o único jeito de
saber que o bucket responde, e com storage remoto significa uma ida à rede por sonda.

## Observabilidade

- **Health check**: `GET /health/` verifica cache e banco. Aceita `?format=json`, `text`,
  `openmetrics`. Retorna 500 se algum check falhar.
- **Logs**: `structlog` em JSON, com correlation id injetado pelo `django-guid` e exposto no
  header `X-Correlation-Id`.
- **Sentry**: ativado fora de `DEBUG` quando `INTEGRATION_SENTRY_DSN` está definido, sem PII
  por padrão (ver [`docs/standards/observability.md`](docs/standards/observability.md)).
- **Prometheus**: com `ENABLE_PROMETHEUS=true`, as métricas ficam em `/monitoring/metrics`.
  `docker compose up -d prometheus` sobe um Prometheus já configurado em
  `tools/prometheus.yml` para raspar a aplicação rodando no host.

## Testes e qualidade

As factories ficam em `apps/<app>/tests/factories.py` e o `conftest.py` da raiz expõe
`user`, `superuser` e `auth_client` para qualquer teste. `UserFactory` passa pelo
`create_user` do manager, não pelo `objects.create` padrão do factory_boy — só ele
faz o hash da senha e cria o `Profile` associado.

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

Instale os hooks de pre-commit uma vez com `pre-commit install`. Eles rodam, a cada commit:
Ruff (`check --fix` e `format`), Biome, o Stylelint da convenção BEM e as verificações de
higiene — newline final, espaço em branco à direita, fim de linha LF e sintaxe de YAML,
TOML e JSON.

Ruff e Biome são hooks `local`, apontando para o binário do projeto: a versão vem do
`uv.lock` e do `bun.lock`, não de um `rev` que envelhece em paralelo. Os hooks do Ruff
usam `--force-exclude` porque o pre-commit passa os arquivos um a um, e sem a flag o Ruff
ignora o `extend-exclude` do `pyproject.toml` e passa a lintar `migrations/`.

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
