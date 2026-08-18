# Padrões: git, commits e CI

## Commits

Conventional Commits, **em português, sem acento, no imperativo**. O assunto diz o efeito,
não o arquivo:

```text
feat(accounts): dar catalogo proprio a cada app
fix(celery): destravar o worker, que nao subia
build(docker): adicionar imagens de dev e producao e o Procfile
test(accounts): cobrir a API de perfil e os presenters
docs(env): adicionar .env.example com todas as variaveis
```

Tipos em uso: `feat`, `fix`, `refactor`, `test`, `docs`, `build`, `chore`. O escopo é o app
ou a área (`accounts`, `core`, `settings`, `frontend`, `i18n`, `docker`, `typing`) e pode
ser omitido quando a mudança é do repositório inteiro.

Um commit resolve uma coisa. Se o assunto precisa de "e" para descrever duas mudanças
independentes, são dois commits. Migration, catálogo `.po` e teste andam **no mesmo commit**
da mudança que os exige — separá-los produz um commit intermediário que não passa no CI.

Corpo é opcional; use-o para o *por que*, quando o assunto não cabe. `sem acento` vale para
a mensagem toda.

## Branches e PR

`master` é o tronco. Trabalho em branch, integrado por PR — o CI roda em push para
`master` e em todo PR.

O [template de PR](../../.github/pull_request_template.md) pede quatro coisas: **o que
muda** (comportamento, não arquivos), **por quê**, **como foi verificado** (o que você
rodou de fato e o que viu) e o checklist. "Testes passam" não conta se a mudança não é
coberta por teste nenhum — nesse caso, diga o que exercitou à mão.

Se o PR toma uma decisão estrutural, ele carrega o ADR (ver
[`docs/adr/`](../adr/README.md)). Se muda uma convenção, carrega a atualização do padrão.

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
