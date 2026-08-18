# Padrões: frontend

O HTML é do Django; o Vite é pipeline de assets; o cliente é enriquecido
progressivamente. Comandos em [`README.md`](../../README.md); os porquês nos
ADRs [0002](../adr/0002-vite-como-pipeline-de-assets-em-backend-integration.md),
[0003](../adr/0003-htmx-stimulus-e-alpine-em-vez-de-uma-spa.md) e
[0006](../adr/0006-django-cotton-para-componentes-de-template.md).

## Onde as coisas moram

```text
frontend/
├── entries/app.js       # único entrypoint; só orquestra
├── lib/                 # módulos com regra, testáveis (ex.: csrf.js)
├── controllers/         # *_controller.js do Stimulus, auto-registrados
└── styles/app.css       # Tailwind + CSS próprio

templates/
├── layouts/base.html    # herança clássica: <head>, assets, csrf-token
├── pages/               # páginas, e pages/partials/ para fragmentos de HTMX
└── components/          # componentes django-cotton (COTTON_DIR)
```

Regra do entrypoint: `app.js` importa e liga, não decide. Qualquer comportamento com
regra — como o header CSRF do HTMX — vira módulo em `lib/`, com teste ao lado
(`*.test.js`).

## Assets: a chave do manifest

`{% vite_css %}`, `{% vite_js %}` e `{% vite_asset %}` recebem **o caminho do input
relativo à raiz do projeto**, que é a chave que o Vite grava no manifest:

```django
{% load vite %}
{% vite_css 'frontend/entries/app.js' %}
{% vite_js 'frontend/entries/app.js' %}
```

A mesma string vale em desenvolvimento (dev server em `:8001`) e em produção (manifest em
`static/dist/.vite/manifest.json`). Entrypoint novo entra em `vite.config.mjs`, em
`build.rollupOptions.input`, e é referenciado pelo caminho — nunca pelo nome do bundle.

Fora de `DEBUG`, renderizar template exige manifest. Por isso a suíte injeta um stub
(`conftest.py`) e os e2e rodam depois de `bun run build`.

## Qual biblioteca usar

| Situação | Ferramenta |
| --- | --- |
| buscar/trocar um pedaço de HTML que o servidor renderiza | HTMX |
| comportamento reutilizável ligado a um pedaço de DOM | Stimulus |
| microestado local: dropdown, toggle, acordeão | Alpine |
| lógica sem DOM (formatação, cálculo, header de request) | módulo em `lib/` |

Na dúvida entre Stimulus e Alpine: se dá vontade de testar, é Stimulus.

**HTMX** — a view devolve fragmento de `templates/pages/partials/`. O CSRF já vai em toda
request unsafe: um listener de `htmx:configRequest` copia `<meta name="csrf-token">` para
`X-CSRFToken`. Não reimplemente isso por view.

**Stimulus** — arquivo `frontend/controllers/<nome>_controller.js`; o identificador sai do
nome (`hello_controller.js` → `data-controller="hello"`), com `_` virando `-`. O registro é
automático, nada a acrescentar em `index.js`.

**Alpine** — funciona em HTML injetado pelo HTMX porque `app.js` chama
`Alpine.initTree(content)` em `htmx.onLoad`. Fragmento novo não precisa de nada; remover
esse gancho quebra todo `x-data` que venha de swap.

## CSS

Tailwind é utility-first e as utilitárias vão no HTML. O CSS próprio do projeto segue
**BEM**, validado pelo Stylelint:

```text
bloco[__elemento][--modificador]      tudo em kebab-case

.card        .card__title        .card--featured        .card__title--muted
```

Rejeitados: `PascalCase`, `camelCase`, `_underscore`, elemento aninhado
(`.card__title__deep`) e modificador duplicado. A regra vive em `.stylelintrc.json` e é
coberta por `frontend/styles/bem.test.js`, que roda contra o arquivo real — mudar a regra
sem atualizar o teste quebra o CI.

Formatação e nomenclatura são ferramentas distintas de propósito: o Biome cuida do formato
(JS, CSS, JSON), o Stylelint da convenção de nomes.

## Templates

- Página herda de um componente de layout (`<c-layouts.app>`, `<c-layouts.guest>`), que por
  sua vez estende `templates/layouts/base.html`.
- Componente Cotton é marcação reutilizável em `templates/components/`, com atributos como
  props e `<c-slot name="...">` para conteúdo. Comportamento não vai no componente — vai
  para Stimulus.
- Fragmento simples e sem contrato pode continuar como `{% include %}`.
- Texto visível é traduzível (`{% translate %}` / `{% blocktranslate %}`).

## JS: estilo

Biome com o preset recomendado, aspas duplas, ponto e vírgula, `trailingCommas: "all"`,
indent 2, largura 100 — tudo automático via `bun run lint:fix`. Imports são organizados
pelo Biome; não ordene à mão. Teste ao lado do código, em `*.test.js`, rodando em Vitest
com `happy-dom`.
