# Spec: <nome da feature>

- **Status**: Rascunho | Aprovada | Implementada | Obsoleta
- **Data**: AAAA-MM-DD
- **Relacionados**: ADR NNNN, `docs/plans/<plano>.md` (opcional)

## Problema

O que não funciona hoje, ou o que não existe. Do ponto de vista de quem usa — sem falar de
solução ainda.

## Resultado esperado

O que passa a ser possível quando isto estiver pronto. Duas ou três frases.

## Comportamento

As regras, uma por item, observáveis de fora. Cada uma deve ser verificável por um teste.

- Quando <condição>, então <resultado>.
- <Ator> pode <ação> apenas se <condição>.
- <Valor> é validado como <regra>; inválido, a resposta é <resultado>.

### Casos de borda

| Caso | Resultado esperado |
| --- | --- |
| <entrada limite> | <o que acontece> |
| <estado concorrente> | <o que acontece> |
| <falha da dependência externa> | <o que acontece> |

### Fora de escopo

O que esta spec deliberadamente **não** cobre, para a implementação não expandir.

## Modelo de dados

Só o que a feature acrescenta ou muda: entidades, campos, relações e restrições. Sem DDL.

## Interface

- **Web**: quais telas, o que cada uma mostra, o que dispara request parcial.
- **API**: rota, método, forma do payload e da resposta, códigos de erro.
- **Permissões**: quem pode o quê.

## Critério de aceite

- [ ] <condição verificável 1>
- [ ] <condição verificável 2>
- [ ] testes cobrindo os casos de borda da tabela acima

## Perguntas abertas

| Pergunta | Quem decide | Status |
| --- | --- | --- |
| <o que ainda não está resolvido> | <pessoa/papel> | aberta |
