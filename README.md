# Django Project Template

Template de projeto Django com foco em organização por domínio, tipagem forte, frontend 
server-rendered moderno e separação clara entre configuração do framework e configuração 
da aplicação. 

## Visão geral

Este template usa Django como backend principal, com a aplicação localizada em `backend/` 
e o módulo de configuração centralizado em `backend/config/`.
O frontend usa Vite com Bun como runtime/package manager, mantendo o Django como responsável 
pela renderização HTML e o Vite como pipeline de assets.
A estratégia de integração com Vite segue o modelo oficial de backend integration 
com dev server em desenvolvimento e `manifest.json` para produção.

## Stack principal

### Backend

- Django 6.x.
- Django Ninja para APIs HTTP tipadas.
- `django-environ` para settings específicos do Django, como `DEBUG`, `SECRET_KEY` e `DATABASE_URL`.
- `pydantic-settings` para configurações específicas da aplicação.
- PyTest para testes.
- Ruff + MyPy + `django-stubs` para linting e tipagem.

### Frontend

- Tailwind CSS para estilização.
- HTMX para interações server-first em HTML.
- Stimulus como camada principal de comportamento JavaScript.
- Alpine.js como opção para microinterações locais simples.
- Vite para bundling e dev server.
- Bun para instalar dependências e executar o pipeline frontend.

## Estrutura do projeto

```text
.
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   ├── test.py
│   │   │   └── production.py
│   │   └── app_settings/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── features.py
│   │       └── integrations.py
│   ├── apps/
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── apps.py
│   │       └── templatetags/
│   │           ├── __init__.py
│   │           └── vite.py
│   ├── templates/
│   └── static/
├── frontend/
│   ├── entries/
│   ├── styles/
│   ├── controllers/
│   └── images/
├── docs/
├── agents/
├── package.json
├── vite.config.mjs
└── pyproject.toml
```

A pasta `backend/` contém apenas o universo Django do projeto, enquanto a raiz do repositório 
pode conter documentação, arquivos de suporte para agentes e outros artefatos sem relação 
direta com o framework.
O módulo `config` concentra bootstrap e configuração do Django, enquanto `apps`, `templates` 
e `static` ficam no mesmo nível dentro de `backend/`.

## Convenções arquiteturais

- `backend/config/settings/`: settings do Django separados por ambiente, mantendo o padrão do framework.
- `backend/config/app_settings/`: configurações específicas da aplicação, tipadas com Pydantic.
- `backend/apps/`: apps de domínio e apps transversais.
- `backend/apps/core/`: utilidades globais, incluindo templatetags compartilhadas, como a integração com Vite.
- `backend/templates/`: templates globais do projeto.
- `backend/static/`: arquivos estáticos servidos pelo Django, incluindo o output do build do Vite.
- `frontend/`: código-fonte do frontend que será processado pelo Vite.

## Settings

Os settings do Django permanecem no formato tradicional em módulos Python, conforme a abordagem 
documentada pelo framework.
Itens como `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, cache, email e segurança 
ficam em `backend/config/settings/` e são lidos com `django-environ`.

As configurações específicas da aplicação ficam em `backend/config/app_settings/`, 
usando `pydantic-settings` para modelagem tipada e validação de variáveis de ambiente.
Exemplos típicos incluem feature flags, URLs de integrações externas, parâmetros de billing, 
timeouts e limites internos da aplicação.

## Frontend

O frontend foi pensado para aplicações Django server-rendered, sem depender de SPA.
A responsabilidade das bibliotecas é dividida da seguinte forma:

- HTMX para requests parciais e atualização de fragmentos HTML vindos do servidor.
- Stimulus para comportamento cliente estruturado e reutilizável.
- Alpine.js apenas para microestado local simples, quando um controller Stimulus seria desnecessário.
- Tailwind CSS para composição visual rápida e consistente.

## Vite + Bun

O Vite é usado no modo recomendado para integração com backend: o template renderiza assets a 
partir do dev server em desenvolvimento e a partir do `manifest.json` em produção.
O Bun funciona com Vite e pode executar o dev server com `bunx --bun vite`, além do build 
com `bunx --bun vite build`.

A library de template tags do Vite deve viver em `backend/apps/core/templatetags/vite.py`, e pode 
expor tags separadas para CSS e JS, por exemplo `{% vite_css %}` e `{% vite_js %}`.

## Instalação

### Requisitos

- Python 3.13+
- Bun
- Banco de dados compatível com a configuração escolhida

### Backend

```bash
uv sync
```

Ou, se preferir outro gerenciador de ambiente, instale as dependências Python 
definidas no `pyproject.toml`.

### Frontend

```bash
bun install
```

## Ambiente local

Crie um arquivo `.env` baseado em `.env.example`.
Variáveis específicas do Django devem ser consumidas pelos settings tradicionais, enquanto 
variáveis de aplicação devem seguir a convenção dos modelos em `app_settings`.

Exemplo mínimo:

```env
DEBUG=true
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## Executando o projeto

### Backend

```bash
python backend/manage.py runserver --settings=config.settings.local
```

### Frontend

```bash
bun run dev
```

O Django continuará servindo HTML e endpoints, enquanto o Vite servirá assets com HMR 
durante o desenvolvimento.

## Build de produção

```bash
bun run build
python backend/manage.py collectstatic --settings=config.settings.production
```

Após o build, o Vite gera os assets compilados e o `manifest.json`, que serão lidos pelas 
template tags no Django.

## Testes e qualidade

### Testes

```bash
pytest
```

### Lint e tipagem

```bash
ruff check . --fix
ruff format .
mypy .
```

Esse fluxo combina linting rápido com Ruff e tipagem estática com MyPy e `django-stubs`, 
o que é especialmente útil em projetos Django com tipagem forte.

## Template tags globais

As templatetags globais devem ficar preferencialmente em `backend/apps/core/templatetags/`, 
já que o Django carrega libraries de custom tags a partir de apps instaladas.
Esse é o local ideal para tags como integração com Vite, helpers de assets, filtros de 
formatação e utilidades de UI compartilhadas.

## Notas finais

Este template foi pensado para favorecer:

- separação clara entre configuração do framework e configuração da aplicação.
- organização por contexto/domínio.
- uso de HTML server-rendered com frontend progressivamente enriquecido.
- uma base sustentável para crescer sem depender de SPA por padrão.