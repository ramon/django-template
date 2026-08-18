# Padrões: quality gates

Um gate aqui é uma checagem local que precisa passar antes de reportar uma tarefa como
concluída ou abrir um PR. Cada gate espelha um job do CI
([`git.md#o-que-o-ci-verifica`](git.md#o-que-o-ci-verifica)) — rodar antes localmente evita
descobrir a falha só depois do push.

Este documento é a referência única de **qual gate se aplica a qual mudança**. O comando
exato de cada gate, nos dois caminhos de desenvolvimento (máquina/container), está em
[`AGENTS.md`](../../AGENTS.md#comandos); não repita a lista aqui.

## Matriz: mudança → gates obrigatórios

| Mudou... | Gates além de lint/typecheck/testes |
| --- | --- |
| Qualquer `.py` de produção | lint (`ruff`), typecheck (`mypy apps tests`), testes (`pytest`) — sempre, é a base |
| `models.py` ou algo que gera migration | + `makemigrations --check --dry-run` limpo |
| String traduzível nova ou alterada (`_()`, `gettext_lazy`, `{% trans %}`) | + `makemessages` rodado e `.po` versionado no commit |
| JS, CSS ou template com classe nova | + `bun run lint && bun run test:coverage`; classe CSS em BEM; piso de cobertura de 90% em `frontend/**/*.js` |
| View, template, fluxo ou controller que chega ao browser | + `pytest -m e2e` (precisa de `bun run build` antes, fora de `DEBUG`) |
| Decisão estrutural (lib nova, camada nova, convenção nova) | + ADR em `docs/adr/` ou padrão revisado, no mesmo commit |
| `pyproject.toml`/`uv.lock` em dependência de produção | + confirmar que ela não vaza para a imagem final (job `docker` do CI, ver [`infra.md`](infra.md)) |
| `Procfile` ou `docker-compose.yml` com processo novo | + paridade entre os dois arquivos ([`infra.md`](infra.md)) |

Mudança só em `docs/`, `tests/` ou config sem efeito em código de produção não aciona os
gates de código, mas ainda passa por lint/format se tocou `.py` de teste.

## Ordem recomendada

Do mais rápido e mais informativo ao mais lento, para falhar cedo:

1. `ruff check` / `ruff format --check`
2. `mypy apps tests`
3. `pytest` (unit primeiro se estiver depurando; a suíte completa antes de reportar)
4. `bun run lint && bun run test:coverage`, se mexeu em JS/CSS
5. `makemessages`/`makemigrations`, se o caso pede — são baratos, mas ficam por último
   porque só fazem sentido depois que o código estabilizou
6. `pytest -m e2e`, por último — é o gate mais lento e o único que builda o frontend

## Por que cada gate existe

- **lint/format**: Ruff e Biome são a fonte de formatação; ajustar espaçamento à mão só
  para o commit divergir do que a ferramenta geraria depois.
- **typecheck**: `mypy` roda `strict`; o job falha em qualquer erro, então não há gate
  "parcial" — ou o módulo tipa limpo, ou fica registrado por que não
  (`# type: ignore[...]  # motivo`).
- **testes**: cobrem regra de negócio, contrato de API e regressão. Ver
  [`testing.md`](testing.md#o-que-vale-a-pena-testar) para o que vale a pena cobrir.
- **cobertura de JS**: `vitest.config.mjs` exige 90% (linhas, statements, funções,
  branches) em `frontend/**/*.js`, exceto o que só orquestra
  (`entries/**`, `controllers/index.js`). `bun run test:coverage` falha abaixo do piso —
  é o mesmo comando que o job `frontend` roda no CI. Ver
  [`testing.md#cobertura-de-js`](testing.md#cobertura-de-js).
- **i18n**: o CI compara o diff dos `.po`; string nova sem `makemessages` no mesmo commit
  quebra o job mesmo com o texto certo no código, porque o catálogo não bate com a fonte.
- **migrations**: `makemigrations --check --dry-run` falha se o model mudou sem gerar
  arquivo — é a garantia de que o schema em disco corresponde ao código.
- **e2e**: só passa por seletor de `name`/`id`/papel ARIA — texto visível quebra a cada
  string traduzida. Ver [`testing.md`](testing.md#testes-ponta-a-ponta).
- **docs**: um ADR ou padrão desatualizado é pior que ausente, porque outro agente o trata
  como verdade atual (ver [`docs/README.md`](../README.md)).

## Quando um gate falha

- **mypy**: não silencie com `Any` ou `type: ignore` sem comentário do porquê ao lado —
  é o padrão dos silenciamentos já existentes no `pyproject.toml`.
- **diff em `.po` inesperado**: normalmente é string editada à mão no código sem rodar
  `makemessages` depois, ou string nova sem passar pelo comando antes do commit.
- **`makemigrations --check` não limpo**: migration esquecida — gere e comite junto da
  mudança de model, nunca em commit separado.
- **BEM (`bem.test.js`)**: classe fora do padrão `bloco__elemento--modificador`; ajustar a
  classe é mais barato que ajustar o teste.

## Checklist final

A lista operacional — o que rodar antes de dizer que uma tarefa terminou — vive em
[`AGENTS.md#antes-de-dizer-que-terminou`](../../AGENTS.md#antes-de-dizer-que-terminou).
Este documento explica *quando* cada item se aplica; aquele lista *o quê* rodar.
