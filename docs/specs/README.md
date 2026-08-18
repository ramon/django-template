# Especificações

Uma spec descreve o comportamento esperado de uma feature: as regras, os casos de borda e
o critério de aceite. Ela é escrita **antes** do código e vale enquanto não for
substituída — divergência entre spec e implementação é bug, não licença para ignorar a
spec.

## Quando escrever

Vale a spec quando a feature tem regra de negócio própria, mais de um caminho, ou
integração com terceiro. Não vale para mudança óbvia de uma tela, correção de bug ou
ajuste de texto — nesses casos o PR já conta a história.

## Como escrever

1. Copie [`TEMPLATE.md`](TEMPLATE.md) para `<nome-em-kebab-case>.md`.
2. Descreva **comportamento observável**, não implementação: "o convite expira em 7 dias",
   não "salvar `expires_at` no model".
3. Liste os casos de borda com o resultado esperado de cada um. É a parte que vira teste.
4. Marque o que está **fora de escopo**, para a feature não crescer no meio do caminho.
5. Deixe as perguntas abertas visíveis, com quem decide, em vez de escolher em silêncio.

## Ciclo de vida

`Rascunho` → `Aprovada` → `Implementada` → `Obsoleta`.

Uma spec implementada continua no repositório: passa a ser a descrição do comportamento
atual, e o lugar onde se verifica se uma mudança futura quebra alguma regra. Feature
removida deixa a spec como `Obsoleta`, com a data e o motivo.

## Índice

Nenhuma spec ainda. Acrescente a linha aqui ao criar a primeira.

| Spec | Status | Data |
| --- | --- | --- |
