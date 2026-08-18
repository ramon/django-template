## O que muda

<!-- O comportamento, não os arquivos. O diff já mostra os arquivos. -->

## Por quê

<!-- O problema que isto resolve. Se for bug, como ele se manifestava. -->

## Como foi verificado

<!--
O que você rodou de fato, e o que viu. "Testes passam" não conta se a mudança
não é coberta por nenhum teste — nesse caso, diga o que exercitou à mão.
-->

## Checklist

- [ ] `uv run pytest` (e `pytest -m e2e`, se a mudança chega ao browser)
- [ ] `uv run ruff check . && uv run ruff format --check .`
- [ ] `uv run mypy apps tests conftest.py`
- [ ] `bun run lint && bun run test`, se mexeu em JS ou CSS
- [ ] `manage.py makemessages`, se acrescentou string traduzível
- [ ] `manage.py makemigrations`, se mexeu em model
- [ ] `docs/` atualizada: ADR em `docs/adr/` se a decisão é estrutural, o padrão em
      `docs/standards/` se a convenção mudou, o plano em `docs/plans/` se o trabalho continua
