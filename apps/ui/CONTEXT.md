# UI

Biblioteca de componentes Cotton genéricos do projeto — vocabulário visual
compartilhado por qualquer template, não só os de autenticação. Não é, em si, uma
capacidade de negócio.

## Language

**Variant** (botão):
Estilo de ênfase do `<c-ui.button>` — `prominent` (preenchido, ação principal),
`outline` (contornado, ação secundária) ou `link` (texto, ação terciária/discreta).
_Avoid_: tipo de botão, estilo

**Color** (botão, badge):
Esquema de cor semântico do componente — `primary`, `secondary` ou `danger`,
mapeado para os tokens de tema (ADR 0012). `danger` é a única cor que também muda o
significado (ação destrutiva), as demais são só ênfase visual.
_Avoid_: tema, cor

**Severity** (alerta):
Classificação de um `<c-ui.alert>` — `info`, `success`, `warning` ou `error`. Decide
cor e ícone; não existe token de tema dedicado a `info`/`success`/`warning`, então o
componente reaproveita `primary`/`secondary`/`tertiary` (ver
`docs/plans/frontend-auth-styling.md`, tabela de decisões).
_Avoid_: tipo de alerta, nível

**Surface role** (painel, card):
Qual `surface-container-*` um bloco usa para se destacar do fundo ao redor — não é
uma prop nomeada, é a escolha de token dentro do componente. Painel usa
`surface-container-low`; nada aqui introduz nome novo além dos tokens da ADR 0012.
_Avoid_: nível de elevação, camada

**Element** (allauth):
Vocabulário do próprio `django-allauth`: cada tela de conta é montada com
`{% element %}` sobre um `{% block content %}` de `allauth/layouts/*.html`. Os
componentes deste app existem para servir de alvo desses overrides
(`allauth/elements/*.html`), mas também são usáveis fora do fluxo de auth.
_Avoid_: widget, componente allauth
