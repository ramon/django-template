# Changelog

Este arquivo segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o
projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/). O processo de
release está documentado em
[`docs/standards/git.md#changelog-e-versionamento`](docs/standards/git.md#changelog-e-versionamento).

## [Unreleased]

### Added

- O manifest do Vite pode ser lido de outro lugar. `settings.VITE_MANIFEST_PATH` troca o
  arquivo (padrão: `static/dist/.vite/manifest.json`), e `settings.VITE_MANIFEST_LOADER`
  aceita o caminho pontilhado de uma função sem argumentos que devolve o manifest já
  parseado, para quando ele não está no disco (bucket, CDN). O padrão é
  `apps.core.templatetags.vite.read_manifest_file`. A tag continua chamando o loader uma
  vez por processo.

### Fixed

- Em produção, cada chunk JS importado era baixado duas vezes. O storage de estáticos
  acrescentava o hash do Django ao nome que o Vite já versiona, e o `{% static %}` devolvia
  esse outro nome: o `modulepreload` baixava uma cópia, e o `import` dentro dos chunks
  baixava a outra, esta com `max-age=60`. O novo `apps.core.storage.ViteManifestStaticFilesStorage`
  publica `dist/` com o nome e o conteúdo que o Vite gerou, sem cópias com hash e sem
  reescrever o `url()` dos CSS de `dist/`. Os arquivos versionados pelo Vite saem com
  `Cache-Control: max-age=315360000, public, immutable` via
  `SERVESTATIC_ADD_HEADERS_FUNCTION`. O resto dos estáticos continua com o hash do Django
  ([ADR 0018](docs/adr/0018-saida-do-vite-publicada-sem-o-hash-do-django.md)).

## [1.3.1] - 2026-09-15

### Changed

- A convenção BEM no CSS passa a ser validada pelo Biome, com o plugin GritQL
  `frontend/styles/bem.grit`, e o Stylelint sai do projeto — dependência,
  `.stylelintrc.json`, script `lint:css` e hook de pre-commit. As regras são as mesmas
  (classe em `bloco[__elemento][--modificador]` e keyframes em kebab-case). O script
  `lint:js` vira `lint:biome`, porque sempre cobriu CSS e JSON também.

### Fixed

- Aninhamento com sufixo do Sass (`.card { &__title {} }`) era aceito pelo Stylelint, mas em
  CSS nativo compila para `__title.card`, um seletor que não casa com nada. O Biome o
  rejeita (`noUnknownTypeSelector`), e o `bem.test.js` agora cobre o caso.

## [1.3.0] - 2026-09-13

### Fixed

- `{% vite_css %}` não emitia, em produção, o CSS de chunks importados pela entrada. Com
  mais de um entrypoint o Rollup move o código comum — e o CSS que ele importa — para um
  chunk compartilhado, e o estilo sumia só em produção. A tag agora segue `imports`
  recursivamente (sem repetir chunk nem arquivo, e à prova de ciclo), emite o CSS das
  dependências antes do da entrada, e `{% vite_js %}` passa a emitir `modulepreload` para
  os chunks importados, como no guia de backend integration do Vite.
- A URL do dev server do Vite estava fixa em `http://127.0.0.1:8001` na templatetag:
  trocar `VITE_PORT` no `.env` mudava a porta publicada pelo compose, mas o browser
  continuava pedindo os assets na 8001. A URL agora vem de
  `settings.VITE_DEV_SERVER_URL` (novo `config/settings/parts/vite.py`), derivada de
  `VITE_PORT` e sobrescrevível pela própria `VITE_DEV_SERVER_URL`; o `vite.config.mjs`
  escuta em `VITE_PORT` e o serviço `frontend` publica a mesma porta dos dois lados.
- O CORS do dev server estava fixo em `http://localhost:8000`, ignorando `APP_PORT`.
  Agora libera `localhost` e `127.0.0.1` na porta de `APP_PORT` — `127.0.0.1` também,
  porque é o endereço que o `runserver` anuncia e o CORS o recusava.

## [1.2.2] - 2026-09-12

### Changed

- `make test-cov` passa a ser um alvo agregador de `make test-cov-py` (pytest com `--cov`)
  e `make test-cov-js` (`bun run test:coverage`), para rodar a cobertura de um lado só sem
  pagar a do outro. `make check` deixa de rodar `test` e `test-cov` em sequência — a suíte
  Python rodava duas vezes — e agora é `lint typecheck test-cov`.
- `docs/standards/testing.md`, `quality-gates.md` e o checklist do `AGENTS.md` passam a
  apontar `make test-cov-py` onde diziam `make test-cov` (a equivalência estava errada: o
  alvo também roda os testes de JS) e a recomendar `make e2e`, que garante o `bun run
  build` antes — sem ele o e2e é pulado, não falha.

## [1.2.1] - 2026-09-10

### Added

- Fronteira de ações de agente no GitHub: agente propõe (abre PR em draft, comenta,
  vincula com `Closes #N`) mas não aprova, não mergeia e não fecha issue; texto de issue e
  de comentário é dado, não instrução. [ADR 0017](docs/adr/0017-fronteira-de-acoes-de-agente-no-github.md)
  e [`docs/standards/git.md#agentes-e-github`](docs/standards/git.md#agentes-e-github),
  com um item novo no template de PR.

### Changed

- A numeração de ADR passa a ter duas faixas: `0001`–`1000` é reservada ao
  `django-template` e **projeto derivado começa no `1001`**. Antes o projeto continuava do
  último número herdado, o que fazia a base e o projeto produzirem o mesmo número e a
  atualização seguinte da base sobrescrever a decisão local. Ver
  [faixas de numeração](docs/adr/README.md#faixas-de-numeração).

## [1.2.0] - 2026-09-03

### Added

- Pytest agora falha abaixo de 90% de cobertura de linhas e 85% de branches em `apps/`,
  avaliados em separado por um hook em `conftest.py` (`--cov-fail-under` do pytest-cov só
  teria um número combinado, que mistura linha e branch numa média ponderada). `make
  test-cov` roda `pytest --cov=apps --cov-branch --cov-report=term-missing` junto do `bun
  run test:coverage`; mesmo comando no CI. Ver
  [`docs/standards/testing.md#cobertura-de-python`](docs/standards/testing.md#cobertura-de-python).

## [1.1.1] - 2026-09-02

### Changed

- `docker-compose.yml` não publica mais `5432`/`6379` no host: `database` e `kv-database`
  só expõem porta com `make services` (que carrega o novo `docker-compose.local-db.yml`).
  `app`, `frontend` e `prometheus` publicam presos a `127.0.0.1` e com a porta vinda do
  `.env` — `APP_PORT`, `VITE_PORT`, `PROMETHEUS_PORT` (mais `POSTGRES_PORT`/`VALKEY_PORT`
  e `COMPOSE_PROJECT_NAME`), para conviver com outra stack Docker sem `port is already
  allocated`. [ADR 0016](docs/adr/0016-portas-do-compose-internas-por-padrao.md) e
  [`docs/standards/infra.md`](docs/standards/infra.md#serviços-e-portas).
- `make services` agora sobe banco e cache com `-f docker-compose.yml -f
  docker-compose.local-db.yml`; `docker compose up -d database` cru não publica porta.

## [1.1.0] - 2026-08-30

### Added

- Convenção de autoria de componentes Cotton, no molde do `django-cotton-ui` (só os
  padrões, sem o kit como dependência):
  [ADR 0015](docs/adr/0015-convencao-de-autoria-de-componentes-cotton.md) e
  [`docs/standards/components.md`](docs/standards/components.md) — `<c-vars>` com `class`,
  variantes como dict, `{{ attrs }}` no controle que submete o valor, e teste de contrato
  por componente em `apps/ui/tests/`.

### Changed

- Todos os `<c-ui.*>` aceitam `class` (aplicada no fim da lista) e abrem com um comentário
  de cabeçalho; a escolha de estilo por variante virou dict + `|get_item` no lugar de
  `{% if %}` aninhado no atributo `class`.
- `<c-ui.table>` passa a estilizar `thead`/`tbody`/`tr`/`th`/`td` como descendentes; esses
  deixaram de ser componentes, assim como `<c-ui.h1>`/`h2`/`p`/`hr` — "uma tag com uma
  classe" fica no call site (nos overrides de `templates/allauth/elements/`).

### Removed

- Componentes `<c-ui.h1>`, `<c-ui.h2>`, `<c-ui.p>`, `<c-ui.hr>`, `<c-ui.thead>`,
  `<c-ui.tbody>`, `<c-ui.tr>`, `<c-ui.th>` e `<c-ui.td>` — sem prop, variante nem reuso
  fora do override de element do allauth.

## [1.0.1] - 2026-08-28

### Changed

- Os testes e2e agora rodam em dois motores por padrão — Chromium e WebKit (Safari) —
  via `--browser chromium --browser webkit` no `addopts`; o CI instala os dois.
- `tests/e2e/` na raiz passa a ser só para fluxo que atravessa mais de um app (ou o shell
  do projeto: layout, tema, admin); e2e preso a um app vive em `apps/<app>/tests/e2e/`. Os
  e2e de auth foram para `apps/accounts/tests/e2e/` e os de home/health para
  `apps/core/tests/e2e/`. A auto-marcação (`e2e` + `django_db`) e o guard de build migraram
  para o `conftest.py` da raiz e valem para qualquer `tests/e2e/`; as fixtures comuns
  (`e2e_page`, `verified_user`, `login`) também são globais agora.
- Plano concluído agora é removido em vez de arquivado — o registro fica no histórico do
  Git e no PR, e decisão estrutural já vira ADR ([`docs/plans/README.md`](docs/plans/README.md)).

### Removed

- Planos já implementados `frontend-auth-styling` e `accounts-signup-name-field`.

## [1.0.0] - 2026-08-22

### Security

- Removido o fallback de avatar para o Gravatar: perfil sem avatar próprio devolvia o
  hash SHA-256 do e-mail do usuário para `gravatar.com` por padrão, sem opção de
  desligar ([ADR 0014](docs/adr/0014-remover-fallback-de-avatar-para-o-gravatar.md)).
  `GET /profile/me` agora devolve `picture` vazio nesse caso.
  **BREAKING CHANGE**: `GET /profile/me` devolve `"picture": ""` para perfil sem avatar,
  em vez de uma URL do Gravatar.

## [0.1.1] - 2026-08-18

### Fixed

- Tornado traduzível o `verbose_name` dos campos de `core` e `accounts`.

### Changed

- Traduzidos para o inglês os nomes de teste de `core`, `accounts` e e2e, e o comando
  `makemessages` customizado.
- Docstrings de `core` e `accounts` alinhadas ao padrão de `backend.md`.
- Estendida a regra de idioma dos padrões para cobrir também os testes.

## [0.1.0] - 2026-08-18

Primeira versão do template: base Django server-rendered com API, frontend
progressivamente aprimorado e a estrutura de documentação para agentes.

### Added

- Projeto Django com `apps/core` e `apps/accounts`, API em django-ninja, Vite como
  pipeline de assets em modo backend integration, e HTMX, Stimulus e Alpine no cliente.
- Autenticação com django-allauth, MFA e CORS liberado para a API.
- `User` e `Profile` customizados, com value objects (`PersonName`, `PhoneNumber`),
  mixins de model reutilizáveis e presenters.
- Sondas de saúde (`/health/`) separadas por propósito, e a primeira task do Celery.
- Catálogo de tradução próprio por app, com `makemessages`/`compilemessages`
  customizados e idempotentes.
- Observabilidade com Sentry (sem envio de PII) e logging estruturado
  (django-structlog).
- Suíte de testes com pytest, cobertura de JS com Vitest e testes ponta a ponta com
  pytest-playwright.
- Imagens Docker de desenvolvimento e produção, `Procfile`, `docker-compose.yml` e
  workflow de CI no GitHub Actions.
- `Makefile` para simplificar o lifecycle de desenvolvimento.
- Estrutura de documentação em `docs/` (`standards/`, `adr/`, `specs/`, `plans/`) e
  `AGENTS.md` como referência canônica para agentes.

[Unreleased]: https://github.com/ramon/django-template/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/ramon/django-template/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/ramon/django-template/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/ramon/django-template/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/ramon/django-template/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ramon/django-template/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/ramon/django-template/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ramon/django-template/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ramon/django-template/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ramon/django-template/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/ramon/django-template/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ramon/django-template/releases/tag/v0.1.0
