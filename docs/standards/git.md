# Padrões: git, commits e CI

## Commits

Conventional Commits, **em português, no imperativo**. O assunto diz o efeito, não o
arquivo:

```text
feat(accounts): dar catálogo próprio a cada app
fix(celery): destravar o worker, que não subia
build(docker): adicionar imagens de dev e produção e o Procfile
test(accounts): cobrir a API de perfil e os presenters
docs(env): adicionar .env.example com todas as variáveis
```

Tipos em uso: `feat`, `fix`, `refactor`, `test`, `docs`, `build`, `chore`. O escopo é o app
ou a área (`accounts`, `core`, `settings`, `frontend`, `i18n`, `docker`, `typing`) e pode
ser omitido quando a mudança é do repositório inteiro.

Um commit resolve uma coisa. Se o assunto precisa de "e" para descrever duas mudanças
independentes, são dois commits. Migration, catálogo `.po` e teste andam **no mesmo commit**
da mudança que os exige — separá-los produz um commit intermediário que não passa no CI.

Corpo é opcional; use-o para o *por que*, quando o assunto não cabe.

## Branches e PR

git-flow (ver [ADR 0009](../adr/0009-adotar-git-flow-para-branches-e-releases.md)). Duas
branches permanentes:

| Branch | Papel | Recebe merge de |
| --- | --- | --- |
| `master` | reflete produção; todo merge aqui é uma versão, com tag `vX.Y.Z` | `release/*`, `hotfix/*` |
| `develop` | integração; é contra ela que se abre PR de trabalho em andamento | `feature/*`, `release/*`, `hotfix/*` |

E três tipos de branch de vida curta:

- **`feature/<escopo>-<descricao>`** — a partir de `develop`, PR de volta para `develop`.
  É a branch padrão de trabalho.
- **`release/X.Y.Z`** — a partir de `develop`, quando o escopo do próximo release fecha.
  Só recebe fix e o trabalho de fechar a versão: bump em `pyproject.toml` e mover
  `Unreleased` do `CHANGELOG.md` para a seção `X.Y.Z` (ver
  [Changelog e versionamento](#changelog-e-versionamento)). Ao terminar: merge em
  `master` com tag `vX.Y.Z`, e merge de volta em `develop`.
- **`hotfix/X.Y.Z`** — a partir de `master`, para corrigir produção sem esperar o próximo
  release. Mesmo destino duplo: merge em `master` com tag, merge de volta em `develop`.

O CI roda em push para `master` e `develop`, e em todo PR.

O [template de PR](../../.github/pull_request_template.md) pede quatro coisas: **o que
muda** (comportamento, não arquivos), **por quê**, **como foi verificado** (o que você
rodou de fato e o que viu) e o checklist. "Testes passam" não conta se a mudança não é
coberta por teste nenhum — nesse caso, diga o que exercitou à mão.

Se o PR toma uma decisão estrutural, ele carrega o ADR (ver
[`docs/adr/`](../adr/README.md)). Se muda uma convenção, carrega a atualização do padrão.

## Changelog e versionamento

[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e
[Semantic Versioning](https://semver.org/lang/pt-BR/). `CHANGELOG.md` na raiz, versão em
`pyproject.toml` (`project.version`), tag `vX.Y.Z` em `master` a cada release.

### Formato do `CHANGELOG.md`

Uma seção `## [Unreleased]` no topo, acumulando entrada conforme o trabalho é integrado
em `develop`. Dentro de cada versão, só as categorias que se aplicam, nesta ordem:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Entrada descreve o
efeito para quem usa ou desenvolve o projeto, não o commit — várias vezes um commit não
gera entrada nenhuma (ver mapeamento abaixo).

### Que commit vira entrada de changelog

O tipo do Conventional Commit indica a categoria; nem todo tipo gera entrada:

| Tipo do commit | Categoria no changelog |
| --- | --- |
| `feat` | `Added` (ou `Changed`, se altera comportamento existente em vez de acrescentar) |
| `fix` | `Fixed` |
| `refactor`, `build` com efeito visível (ex: mudança de imagem publicada) | `Changed` |
| commit com `BREAKING CHANGE:` no rodapé, ou `!` depois do tipo/escopo (`feat!:`) | entra na categoria normal, mas com o texto do `BREAKING CHANGE` destacado — é o que força bump major |
| correção de vulnerabilidade | `Security` |
| `test`, `docs`, `chore`, `ci`, `style` sem efeito observável | nenhuma — fica só no `git log` |

### Versionamento

`MAJOR.MINOR.PATCH`. O tipo do commit (ou a presença de `BREAKING CHANGE`) determina o
bump, do maior para o menor — um `BREAKING CHANGE` sozinho já decide, mesmo que o release
também tenha `feat` e `fix`:

- `BREAKING CHANGE` (rodapé) ou `!` depois do tipo/escopo → **major**
- `feat` → **minor**
- `fix` e demais tipos com efeito de usuário (`Changed`, `Security`) → **patch**

### Processo de release

Dentro de `release/X.Y.Z` (ou `hotfix/X.Y.Z`):

1. Mover as entradas de `## [Unreleased]` para uma seção nova `## [X.Y.Z] - AAAA-MM-DD`.
2. Bumpar `project.version` em `pyproject.toml` para `X.Y.Z`.
3. Commitar as duas mudanças juntas: `chore(release): bump version to X.Y.Z`.
4. Merge em `master`, tag `vX.Y.Z` na cabeça de `master`, merge de volta em `develop`.

## Pre-commit

Instale uma vez:

```bash
pre-commit install
```

A cada commit roda: Ruff (`check --fix` e `format`), Biome nos JS/CSS/JSON alterados, o
Stylelint da convenção BEM e a higiene de arquivo — newline final, espaço à direita, fim
de linha LF e sintaxe de YAML, TOML e JSON.

Dois detalhes deliberados no `.pre-commit-config.yaml`:

- Ruff e Biome são hooks **`local`**, apontando para o binário do projeto: a versão vem do
  `uv.lock` e do `bun.lock`, não de um `rev` que envelhece em paralelo e formata diferente.
- Os hooks do Ruff usam **`--force-exclude`**, porque o pre-commit passa os arquivos um a
  um e sem a flag o Ruff ignora o `extend-exclude` do `pyproject.toml` e passa a lintar
  `migrations/`.

## O que o CI verifica

`.github/workflows/ci.yml`:

| Job | O que valida |
| --- | --- |
| `lint` | `ruff check` e `ruff format --check` |
| `test` | `manage.py check` nos três cenários, migrations em dia, catálogos em dia, `pytest` com cobertura contra Postgres e Valkey |
| `frontend` | Biome, Stylelint (BEM), Vitest com o piso de cobertura, `vite build` e a presença do manifest |
| `e2e` | `pytest -m e2e` num Chromium real; anexa `test-results/` se falhar |
| `docker` | build da imagem de produção, ausência de ferramenta de build e de dependência de dev, e a imagem subindo e respondendo `/health/` |
| `typecheck` | `mypy apps tests` em modo strict |

Rodar localmente o equivalente, antes de abrir o PR:

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy apps tests
uv run pytest
bun run lint && bun run test:coverage
python manage.py makemessages && git diff --exit-code -- '*.po'
python manage.py makemigrations --check --dry-run
```

## Nunca comite

`.env`, `.mo`, `static/dist/`, `public/static/`, `public/media/`, `test-results/`,
`.coverage`, `node_modules/`. O `.gitignore` cobre todos — se um deles aparece no `git
status`, o problema é o caminho do arquivo, não o `.gitignore`.
