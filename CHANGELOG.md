# Changelog

Este arquivo segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o
projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/). O processo de
release está documentado em
[`docs/standards/git.md#changelog-e-versionamento`](docs/standards/git.md#changelog-e-versionamento).

## [Unreleased]

### Security

- Removido o fallback de avatar para o Gravatar: perfil sem avatar próprio devolvia o
  hash SHA-256 do e-mail do usuário para `gravatar.com` por padrão, sem opção de
  desligar ([ADR 0014](docs/adr/0014-remover-fallback-de-avatar-para-o-gravatar.md)).
  `GET /profile/me` agora devolve `picture` vazio nesse caso.

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

[Unreleased]: https://github.com/ramon/django-template/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/ramon/django-template/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ramon/django-template/releases/tag/v0.1.0
