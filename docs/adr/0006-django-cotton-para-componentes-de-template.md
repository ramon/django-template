# 0006. django-cotton para componentes de template

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0003, `docs/standards/frontend.md`

## Contexto

Com o HTML vindo do servidor ([0003](0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md)),
a reutilização de marcação passa a ser um problema de template. As ferramentas nativas do
Django resolvem mal os dois casos mais comuns: `{% include %}` recebe contexto por
`with`, sem contrato nem valor padrão, e não aceita conteúdo aninhado; `{% block %}` só
funciona por herança, que é vertical — não serve para um cartão usado três vezes na mesma
página. Uma inclusion tag resolve, mas exige uma função Python por componente visual.

## Decisão

Componentes de template usam `django-cotton`. Eles vivem em `templates/components/`
(`COTTON_DIR = "components"`, com `COTTON_SNAKE_CASED_NAMES = True`) e são usados como
tags HTML, com atributos como props e slots nomeados para conteúdo:

```django
<c-layouts.app>
  <c-slot name="header">…</c-slot>
  …
</c-layouts.app>
```

Os layouts do projeto são componentes (`templates/components/layouts/app.html`,
`guest.html`) construídos sobre o `templates/layouts/base.html`, que continua sendo um
template de herança clássica — é onde ficam `<head>`, os assets do Vite e o
`<meta name="csrf-token">`.

A divisão de pastas em `templates/`: `layouts/` para a base herdada, `pages/` para páginas
e `components/` para componentes Cotton.

## Consequências

- **Positivas**: componente visual é um arquivo HTML, sem Python; slots resolvem conteúdo
  aninhado, que o `{% include %}` não faz; a marcação de uso fica legível para quem
  conhece HTML.
- **Negativas**: uma dependência a mais no caminho de renderização, e uma sintaxe que não
  é Django puro — quem chega precisa saber que `<c-…>` não é HTML nativo. Erro em
  componente aparece em stack trace de template, que é menos direto que o de uma tag
  Python.
- **Neutras**: `{% include %}` e herança continuam disponíveis e válidos onde já bastam.

## Alternativas consideradas

### `{% include %}` com `with`

Sem contrato de props, sem default e sem slot. Funciona para fragmento simples, e continua
sendo usado nesses casos — mas não para componente com conteúdo.

### Inclusion tags

Dão contrato e default, ao custo de uma função Python e um registro por componente. Peso
demais para marcação sem lógica.

### django-components

Mais poderoso (componente com classe Python, CSS/JS por componente), e por isso mesmo mais
pesado: o projeto quer componente de marcação, e comportamento já tem casa no Stimulus.
