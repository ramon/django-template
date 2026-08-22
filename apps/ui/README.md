# UI

Componentes Cotton genéricos do projeto — botão, campo, painel, alerta, tabela e
afins — no vocabulário visual e nos tokens de tema já estabelecidos por
`templates/pages/home.html` (ADR 0012). Não é um domínio de negócio: existe para dar
um lugar formal a marcação reutilizável, evitando que cada página reimplemente o
mesmo botão ou o mesmo card.

Para o vocabulário dos próprios componentes (variante, cor, severidade), veja
[`CONTEXT.md`](CONTEXT.md).

## O que tem aqui

- **Componentes de conteúdo**: `<c-ui.button>`, `<c-ui.button_group>`,
  `<c-ui.field>`, `<c-ui.form>`, `<c-ui.panel>`, `<c-ui.alert>`, `<c-ui.badge>`,
  título/parágrafo/divisor (`<c-ui.h1>`, `<c-ui.h2>`, `<c-ui.p>`, `<c-ui.hr>`),
  tabela (`<c-ui.table>` e afins) e `<c-ui.provider_list>` — todos em
  `apps/ui/templates/components/ui/`.
- **Alvo do override de `django-allauth`**: `allauth/elements/*.html` e
  `allauth/layouts/*.html` (ver [ADR 0013](../../docs/adr/0013-customizacao-de-ui-do-allauth-via-elements-e-apps-ui.md))
  delegam para estes componentes, o que estiliza as ~80 páginas do allauth
  sobrescrevendo ~15 arquivos.

## Para quem for mexer aqui

Referência da interface pública (props de cada componente) fica em
[`AGENTS.md`](AGENTS.md). Convenções de template/CSS ficam em
[`docs/standards/frontend.md`](../../docs/standards/frontend.md).
