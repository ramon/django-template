# Planos

Um plano é o estado de um trabalho que não cabe em uma sessão: as etapas, o que já foi
feito, o que sobrou e as decisões tomadas no caminho. Existe para que a próxima sessão —
sua ou de um agente — retome do ponto real, não do zero.

## Quando escrever

Quando o trabalho tem mais de três ou quatro etapas com dependência entre elas, atravessa
várias áreas do projeto (backend + frontend + infra), ou vai ser retomado depois. Tarefa de
uma sessão não precisa de plano; o PR já a descreve.

## Como usar

1. Copie [`TEMPLATE.md`](TEMPLATE.md) para `<nome-em-kebab-case>.md`.
2. Quebre em etapas que terminam em algo verificável — "endpoint respondendo com teste
   passando", não "mexer no model".
3. **Atualize o plano enquanto trabalha**, não no fim: marque a etapa concluída, anote o
   que mudou de rumo e por quê. Plano que só descreve a intenção original é pior que
   nenhum, porque a próxima sessão confia nele.
4. Ao terminar, marque `Concluído` com a data. O arquivo fica no repositório: é o registro
   de como o trabalho aconteceu.

## Ciclo de vida

`Em andamento` → `Concluído` | `Abandonado`.

Plano abandonado fica, com o motivo em uma linha — evita que alguém recomece a mesma coisa
sem saber por que parou.

## Relação com spec e ADR

- A **spec** diz o que precisa acontecer; o **plano** diz em que ordem e o que já
  aconteceu.
- Decisão estrutural que aparecer durante a execução sai do plano e vira **ADR** —
  o plano fica com o link, não com o argumento inteiro.

## Índice

| Plano | Status | Início | Fim |
| --- | --- | --- | --- |
| [Estilizar o fluxo de autenticação do allauth](frontend-auth-styling.md) | Concluído | 2026-08-22 | 2026-08-22 |
| [Corrigir o cadastro (HTTP 500 por falta de nome)](accounts-signup-name-field.md) | Em andamento | 2026-08-22 | — |
