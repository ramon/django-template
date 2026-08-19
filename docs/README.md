# Documentação

Esta pasta é a referência de trabalho do projeto — para pessoas e para agentes. O
[`README.md`](../README.md) da raiz responde *como rodar*; aqui fica *como decidimos* e
*como se escreve código aqui*.

## O que vive onde

| Pasta | Guarda | Pergunta que responde |
| --- | --- | --- |
| [`standards/`](standards/) | convenções de código, por área | "como se faz isso neste projeto?" |
| [`adr/`](adr/) | decisões arquiteturais registradas | "por que está assim?" |
| [`specs/`](specs/) | especificações de features | "o que exatamente precisa acontecer?" |
| [`plans/`](plans/) | planos de implementação em andamento | "onde este trabalho parou?" |

### `standards/` — padrões

Regras estáveis, escritas no presente, sobre como o código é organizado e nomeado.
Muda pouco, e quando muda o código muda com ela.

- [`backend.md`](standards/backend.md) — camadas de um app, models, domínio, serviços,
  presenters, API, settings
- [`frontend.md`](standards/frontend.md) — Vite, HTMX, Stimulus, Alpine, templates, BEM
- [`testing.md`](standards/testing.md) — layout da suíte, factories, fixtures, e2e
- [`i18n.md`](standards/i18n.md) — catálogos por app, `makemessages`/`compilemessages`,
  precedência
- [`infra.md`](standards/infra.md) — compose, imagens, processos, variáveis, sondas
- [`git.md`](standards/git.md) — commits, branches, PR, pre-commit, CI
- [`quality-gates.md`](standards/quality-gates.md) — qual gate cada mudança exige, ordem
  de execução

### `adr/` — Architecture Decision Records

Uma decisão por arquivo, imutável depois de aceita: se a decisão muda, escreve-se um ADR
novo que substitui o anterior. É o lugar onde fica o *motivo* — inclusive o das
alternativas descartadas, que é o que evita alguém "consertar" de volta o que foi
escolhido de propósito. Índice e regras em [`adr/README.md`](adr/README.md).

### `specs/` — especificações

O comportamento esperado de uma feature antes de existir código: regras, casos de borda,
critérios de aceite. Enquanto vale, uma spec ganha do código — divergência é bug.
Convenções em [`specs/README.md`](specs/README.md).

### `plans/` — planos

Trabalho que não cabe em uma sessão: as etapas, o estado de cada uma e as decisões
tomadas no caminho. Um plano é vivo — atualize-o enquanto trabalha e arquive-o quando
terminar. Convenções em [`plans/README.md`](plans/README.md).

## Regras da pasta

- **O que está aqui foi herdado da base e vale por padrão.** `standards/` e os ADRs
  0001–0006 vieram do `django-template`: descrevem como este projeto funciona hoje, não
  uma sugestão. Divergir é legítimo — desde que a divergência seja registrada (ADR novo, ou
  padrão atualizado) no mesmo commit que a introduz.
- **Uma fonte por fato.** Setup, comandos e stack ficam no `README.md` da raiz; daqui a
  gente linka. Duplicar cria duas versões que divergem.
- **Documento desatualizado é pior que documento ausente**, porque agentes tratam o que
  está aqui como verdade. Se a mudança de código contradiz um documento, atualize os dois
  no mesmo commit.
- **Português** na prosa; nomes de arquivo em `kebab-case` sem acento.
- **Data absoluta** (`2026-08-18`), nunca "semana passada".
- **Linka o código** por caminho (`apps/core/templatetags/vite.py`), não por cópia:
  trecho copiado envelhece em silêncio.
