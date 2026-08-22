# Plano: estilizar o fluxo de autenticação do allauth (login, MFA, WebAuthn, sessões)

- **Status**: Em andamento
- **Início**: 2026-08-22
- **Última atualização**: 2026-08-22
- **Relacionados**: ADR [0013](../adr/0013-customizacao-de-ui-do-allauth-via-elements-e-apps-ui.md),
  ADR [0012](../adr/0012-tema-com-tokens-no-molde-do-material-design-3.md),
  ADR [0007](../adr/0007-autenticacao-com-django-allauth-e-mfa.md),
  `docs/standards/frontend.md`, `docs/standards/auth.md`

## Objetivo

Toda tela servida por `django-allauth` (entrada, MFA/WebAuthn, sessões, conexões sociais)
usa os tokens de tema do projeto e um conjunto de componentes Cotton genéricos novos
(`apps/ui/`), em vez dos templates padrão sem estilo do allauth. Os componentes ficam
disponíveis para qualquer página do projeto, não só as de auth.

## Contexto

`django-allauth` (ADR 0007) está instalado com `mfa` (TOTP, WebAuthn, recovery codes) e
`socialaccount`, mas renderiza com os templates próprios da biblioteca — nenhum toque do
design do projeto. O allauth moderno monta cada página com `{% element %}`
(`allauth/elements/*.html`) sobre um layout (`allauth/layouts/{base,entrance,manage}.html`):
sobrescrever esses ~15 arquivos estiliza as ~80 páginas de uma vez (ver ADR 0013).

O projeto já tem tokens de tema M3 com dark mode (ADR 0012, `frontend/styles/app.css`) e um
vocabulário visual de referência em `templates/pages/home.html` (card, botão, pill, chip),
mas nenhum componente Cotton genérico ainda — só os layouts `guest`/`app`, vazios, e o
toggle de tema duplicado ad-hoc dentro de `home.html`.

Fora não instalado: `allauth.idp` e o `openid` legado — não entram no trabalho.

## Etapas

- [ ] **1. Scaffold de `apps/ui`** — app Django sem models, registrado em `INSTALLED_APPS`
      (`config/settings/parts/django.py` ou onde os apps do projeto entram), com
      `apps/ui/templates/components/ui/` e o trio `CONTEXT.md`/`README.md`/`AGENTS.md` ·
      verificação: `uv run python manage.py check` sem erro; entrada nova em
      `CONTEXT-MAP.md`.
- [ ] **2. Componentes Cotton genéricos** — `<c-ui.button>` (variantes prominent/outline,
      primary/secondary, disabled), `<c-ui.field>` (text/textarea/checkbox/radio/password,
      label, help_text, erro), `<c-ui.form>`, `<c-ui.panel>`, `<c-ui.alert>` (severidade
      info/success/warning/error), `<c-ui.h1>`/`<c-ui.h2>`/`<c-ui.p>`/`<c-ui.hr>`,
      `<c-ui.button_group>`, `<c-ui.badge>`, tabela (`table`/`thead`/`tbody`/`tr`/`th`/`td`),
      `<c-ui.provider_list>` — depende de 1 · verificação: `bun run lint:classes` limpo nos
      arquivos novos (classes Tailwind ordenadas).
- [ ] **3. Controller de mostrar/ocultar senha** —
      `frontend/controllers/password_visibility_controller.js` + teste, ligado a
      `<c-ui.field type="password">` — depende de 2 · verificação: `bun run test`.
- [ ] **4. Header/nav centralizados nos layouts** — `templates/components/layouts/guest.html`
      ganha header com logo placeholder + toggle de tema; `app.html` ganha o mesmo header
      mais uma sidebar de "configurações de conta" (Segurança, Sessões, Conexões,
      E-mail/Senha) no slot `sidebar` — depende de 2 · verificação: `templates/pages/home.html`
      atualizado para não duplicar mais o toggle, renderiza igual visualmente
      (`python manage.py runserver` + inspeção manual).
- [ ] **5. Override de `allauth/layouts/*.html`** — `base.html`/`entrance.html` estendem
      `<c-layouts.guest>`, `manage.html` estende `<c-layouts.app>` (populando a sidebar) —
      depende de 4 · verificação: `account_login` renderiza dentro do layout `guest`.
- [ ] **6. Override de `allauth/elements/*.html`** — cada element delega para o componente
      `ui` correspondente, usando `attrs.tags` do allauth para variante (`prominent`,
      `outline`, `primary`) — depende de 2, 5 · verificação: `account/login.html` (sem
      override próprio) já sai estilizado.
- [ ] **7. Varredura de páginas sem cobertura de elements** — checar cada template em
      `account/`, `mfa/`, `socialaccount/`, `usersessions/` que usa HTML fora dos elements
      (ex.: `usersessions/usersession_list.html`, `mfa/webauthn/authenticator_list.html`,
      `account/email.html`) e decidir override pontual quando necessário — depende de 6 ·
      verificação: inspeção manual de cada URL listada no objetivo (login, signup, logout,
      reset de senha, verificação de e-mail, login por código, MFA index, TOTP, WebAuthn
      add/list, recovery codes, reauthenticate, trust device, sessões, conexões sociais).
- [ ] **8. i18n** — `makemessages` para qualquer string nova (header, sidebar, componentes)
      — depende de 4, 7 · verificação: `python manage.py makemessages` sem diff pendente
      além do esperado, catálogos `.po` no commit.
- [ ] **9. e2e smoke** — `tests/e2e/test_auth_*.py` cobrindo as telas renderizáveis sem
      hardware (login, signup, password reset, MFA index, recovery codes); WebAuthn real
      fica de fora (exigiria virtual authenticator do CDP) — depende de 7 ·
      verificação: `uv run pytest -m e2e` (após `bun run build`).
- [ ] **10. Docs de padrão** — `docs/standards/frontend.md` ganha a seção de override de
      allauth via `elements`/`layouts` + `apps/ui`; `docs/standards/auth.md` perde a
      ressalva de "UI é a do allauth, sem estilo" — depende de 9 · verificação: revisão de
      texto.
- [ ] **11. Fechamento** — checklist de qualidade completo (`docs/standards/quality-gates.md`),
      PR para `develop`.

## Estado atual

- **Feito**: ADR 0013 escrito e indexado; branch `feature/frontend-auth-styling` criada a
  partir de `develop`; este plano.
- **Em andamento**: nenhuma etapa de código iniciada ainda.
- **Próximo passo**: etapa 1 (scaffold de `apps/ui`).

## Decisões tomadas no caminho

| Data | Decisão | Motivo | Virou ADR? |
| --- | --- | --- | --- |
| 2026-08-22 | Override de `allauth/elements`+`layouts` em vez de página por página, delegando para `apps/ui` | Estiliza ~80 páginas sobrescrevendo ~15 arquivos; app próprio por exigência do `AGENTS.md` para app novo | [0013](../adr/0013-customizacao-de-ui-do-allauth-via-elements-e-apps-ui.md) |
| 2026-08-22 | JS de WebAuthn/passkey do allauth fica intocado | Superfície de segurança já madura e mantida upstream (ADR 0007) | não |
| 2026-08-22 | Sem HTMX no fluxo de auth | Views do allauth são POST/redirect clássico; forçar swap parcial é briga com a biblioteca | não |
| 2026-08-22 | e2e cobre só telas sem dependência de hardware (nível "a") | Virtual authenticator de WebAuthn via CDP adiciona setup desproporcional ao ganho agora | não |

## Riscos e pontos de atenção

- Nem toda página do allauth passa 100% pelos `elements` (ex.: listas com `<table>` em
  `usersessions`, formulário de WebAuthn com JS embutido) — a etapa 7 pode revelar overrides
  pontuais de página, além do trabalho de `elements`/`layouts`.
- `attrs.tags` do allauth (`"prominent,login,outline,primary"`) precisa de um mapeamento
  claro para variante do `<c-ui.button>` — se o vocabulário de tags do allauth não cobrir
  todas as variantes que `home.html` já usa, decidir na hora (registrar aqui, não miscelânea
  no código).
- `apps/ui` sem nenhum model pode soar estranho no admin/checks — confirmar que
  `python manage.py check` não reclama de app sem `models.py`.

## Fora de escopo

- Dark mode como funcionalidade nova — já vem de graça pelos tokens (ADR 0012); nenhum
  trabalho extra de tema aqui.
- Provedores sociais concretos (Google, GitHub etc.) — `SOCIALACCOUNT_PROVIDERS` continua
  vazio; só o *chrome* das telas de conexão social é estilizado.
- Teste e2e de WebAuthn real (hardware ou virtual authenticator).
- MFA obrigatório para qualquer grupo de usuário — decisão de projeto, não do template
  (ADR 0007).
