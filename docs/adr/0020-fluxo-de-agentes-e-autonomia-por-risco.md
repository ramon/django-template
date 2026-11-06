# 0020. Fluxo de agentes com autonomia proporcional ao risco

- **Status**: Aceito
- **Data**: 2026-11-06
- **Relacionados**: [0017](0017-fronteira-de-acoes-de-agente-no-github.md), [`docs/standards/agent-workflow.md`](../standards/agent-workflow.md), [`docs/standards/git.md`](../standards/git.md)

## Contexto

O projeto já define gates locais e de CI, mas não define papéis para delegar implementação,
revisão técnica, segurança e classificação de risco. Codex e Claude Code aceitam definições
de agente em formatos próprios, então manter prompts completos separados cria risco de
divergência. A [ADR 0017](0017-fronteira-de-acoes-de-agente-no-github.md) exige revisão humana
para todo merge, inclusive mudanças triviais; a nova política busca reduzir esse atrito em
mudanças de baixo risco e preservar revisão humana para mudanças críticas.

## Decisão

Usamos um fluxo comum de implementação e três gates (`G1` qualidade, `G2` código e segurança,
`G3` risco), definido em `docs/standards/agent-workflow.md`, com configurações específicas
para Codex em `.agents/agents/` e Claude Code em `.claude/agents/` que apontam para esse
contrato.

O agente principal orquestra o trabalho; agentes de implementação editam arquivos. O merge
depende do risco: `low` pode ser feito pelo agente principal depois de G1 passar, G2 não ter
achados bloqueadores e G3 registrar a classificação; `medium` exige parecer favorável do
`cto-reviewer` além dos mesmos gates; `high` exige decisão humana e não pode ser mergeado por
agente. Pagamento, autenticação, autorização e migrations são sempre `high`; risco incerto
também sobe para `high`.

## Consequências

- **Positivas**: trabalho de implementação e revisão fica separado; gates deixam resultados
  verificáveis; mudanças de baixo risco podem avançar sem espera por revisão humana; mudanças
  críticas preservam decisão humana.
- **Negativas**: agentes podem consumir mais contexto e tokens; o agente principal continua
  responsável por classificar corretamente o encaminhamento; um agente CTO não oferece a
  independência de uma revisão humana.
- **Neutras**: arquivos de agente são duplicados em formato entre harnesses, mas os contratos
  detalhados permanecem em uma fonte canônica comum; a política depende de proteção de branch
  e permissões adequadas para ser aplicada tecnicamente.

## Alternativas consideradas

### Manter revisão e merge humanos para todos os PRs

Preserva a política da ADR 0017, mas mantém o mesmo custo operacional para mudanças triviais
e mudanças que alteram autenticação, autorização, pagamento ou schema.

### Deixar classificação e merge ao julgamento do agente principal

Reduz a quantidade de papéis, mas não produz um registro independente de revisão e mistura
implementação, classificação e publicação na mesma função.

### Usar um único formato de arquivo para os dois harnesses

Codex e Claude Code carregam configurações distintas; um formato universal não oferece a
mesma descoberta e controle de ferramentas nos dois. Mantemos conteúdo canônico compartilhado
e adaptadores pequenos para cada ferramenta.
