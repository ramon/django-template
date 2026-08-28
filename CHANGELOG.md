# Changelog

Este arquivo segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o
projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/). O processo de
release está documentado em
[`docs/standards/git.md#changelog-e-versionamento`](docs/standards/git.md#changelog-e-versionamento).

## [Unreleased]

### Changed

- Os testes e2e agora rodam em dois motores por padrão — Chromium e WebKit (Safari) —
  via `--browser chromium --browser webkit` no `addopts`; o CI instala os dois.
- `tests/e2e/` na raiz passa a ser só para fluxo que atravessa mais de um app (ou o shell
  do projeto: layout, tema, admin); e2e preso a um app vive em `apps/<app>/tests/e2e/`. Os
  e2e de auth foram para `apps/accounts/tests/e2e/` e os de home/health para
  `apps/core/tests/e2e/`. A auto-marcação (`e2e` + `django_db`) e o guard de build migraram
  para o `conftest.py` da raiz e valem para qualquer `tests/e2e/`; as fixtures comuns
  (`e2e_page`, `verified_user`, `login`) também são globais agora.

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

[Unreleased]: https://github.com/ramon/django-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ramon/django-template/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/ramon/django-template/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ramon/django-template/releases/tag/v0.1.0
