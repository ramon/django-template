# UI — referência para agentes

Interface pública dos componentes Cotton genéricos, para consultar antes de abrir
cada `.html`. Vocabulário de domínio em [`CONTEXT.md`](CONTEXT.md), visão geral
humana em [`README.md`](README.md), convenções de template/CSS em
[`docs/standards/frontend.md`](../../docs/standards/frontend.md).

Atualize esta página no mesmo commit que adicionar um componente, mudar uma prop ou
remover algo listado aqui.

Todo componente aceita atributos HTML nativos extras via passthrough (`id`, `name`,
`data-*`, `hx-*`, `aria-*`...) — não precisam ser declarados aqui, só as props com
comportamento próprio.

## Componentes — `apps.ui.templates.components.ui`

- **`<c-ui.button>`** — `variant` (`prominent` padrão, `outline`, `link`), `color`
  (`primary` padrão, `secondary`, `danger`), `type` (`button` padrão), `href`
  (presente ⇒ renderiza `<a>` em vez de `<button>`). `disabled` é passthrough nativo.
- **`<c-ui.button_group>`** — `vertical` (`False` padrão): empilha os botões do slot
  em coluna em vez de linha.
- **`<c-ui.field>`** — `type` (`text` padrão; `checkbox`/`radio`/`textarea` mudam o
  layout), `label`, `help_text`, `errors` (iterável de mensagens), `value`, `rows`
  (`3`, só `textarea`), `hide_label` (`False` padrão — `True` mantém o `<label>` no
  DOM para leitor de tela, só visualmente oculto via `sr-only`, para formulário que
  usa `placeholder` no lugar de rótulo visível). `label`/`help_text` aceitam prop ou
  `<c-slot name="label">`/`<c-slot name="help_text">` — mesmo nome, o slot tem
  prioridade quando presente. `type="password"` já vem com o botão de mostrar/ocultar
  (`password_visibility_controller.js`, `frontend/controllers/`) embutido.
- **`<c-ui.form>`** — `method` (`post` padrão), `action`. Slot default é o corpo;
  `<c-slot name="actions">` vira uma faixa alinhada à direita abaixo do corpo.
- **`<c-ui.panel>`** — `title`. Slot default é o corpo; `<c-slot name="actions">`
  vira uma faixa de botões abaixo do corpo.
- **`<c-ui.alert>`** — `severity` (`info` padrão, `success`, `warning`, `error`).
  `success`/`warning` reaproveitam os tokens `secondary`/`tertiary` (ver
  `docs/plans/frontend-auth-styling.md`, tabela de decisões — não existe token
  `success`/`warning` dedicado, ADR 0012).
- **`<c-ui.badge>`** — `color` (`neutral` padrão, `primary`, `success`, `warning`,
  `danger`). Mesmo mapeamento de cor do `<c-ui.alert>`.
- **`<c-ui.h1>` / `<c-ui.h2>` / `<c-ui.p>` / `<c-ui.hr>`** — tipografia base, sem
  props próprias.
- **Tabela**: `<c-ui.table>` (envolve em `overflow-x-auto`), `<c-ui.thead>`,
  `<c-ui.tbody>`, `<c-ui.tr>`, `<c-ui.th>`, `<c-ui.td>` (prop `align="right"`).
- **`<c-ui.provider_list>`** — `<ul>` para links de provedor social; cada item é um
  `<li>` de marcação livre do chamador (sem `<c-ui.provider>` — só um `<a>` simples,
  estilizado direto no override do allauth).

## Templatetags — `{% load ui %}` (`apps.ui.templatetags.ui`)

Usadas pelos overrides de `templates/allauth/elements/*.html` para traduzir `attrs`
de um `{% element %}` do allauth em props de componente — não são de uso geral fora
desse contexto.

- `{% button_variant tags as v %}` / `{% button_color tags as c %}` — leem
  `attrs.tags` (lista) e resolvem `variant`/`color` de `<c-ui.button>`.
- `tags|tag_color` — mesma ideia para `color` de `<c-ui.badge>`/severidade de
  `<c-ui.alert>` (primeira tag reconhecida, `neutral` se nenhuma bater).
- `attrs|without_tags` — copia de `attrs` sem a chave `tags` (que é lista Python, não
  serializa em atributo HTML) — usar antes de `:attrs="…"` num componente.
- `bound_field|field_attrs` — monta o dict de `:attrs` de `<c-ui.field>` a partir de
  um `BoundField` (usado por `allauth/elements/fields.html` para render por-campo).
- `{% field_hide_label bound_field unlabeled as h %}` — decide `hide_label`: nunca
  para checkbox/radio, mesmo com `unlabeled=True` (sem `placeholder` como
  alternativa visual ao rótulo).

## Controllers Stimulus ligados a estes componentes

Ficam em `frontend/controllers/` (não organizados por app, ver ADR 0013):

- `password_visibility_controller.js` — alterna `<c-ui.field type="password">` entre
  oculto e visível.
