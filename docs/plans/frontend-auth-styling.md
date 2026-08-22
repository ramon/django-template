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

- [x] **1. Scaffold de `apps/ui`** — app Django sem models, registrado em `INSTALLED_APPS`
      (`config/settings/parts/django.py` ou onde os apps do projeto entram), com
      `apps/ui/templates/components/ui/` e o trio `CONTEXT.md`/`README.md`/`AGENTS.md` ·
      verificação: `uv run python manage.py check` sem erro; entrada nova em
      `CONTEXT-MAP.md`.
- [x] **2. Componentes Cotton genéricos** — `<c-ui.button>` (variantes prominent/outline,
      primary/secondary, disabled), `<c-ui.field>` (text/textarea/checkbox/radio/password,
      label, help_text, erro), `<c-ui.form>`, `<c-ui.panel>`, `<c-ui.alert>` (severidade
      info/success/warning/error), `<c-ui.h1>`/`<c-ui.h2>`/`<c-ui.p>`/`<c-ui.hr>`,
      `<c-ui.button_group>`, `<c-ui.badge>`, tabela (`table`/`thead`/`tbody`/`tr`/`th`/`td`),
      `<c-ui.provider_list>` — depende de 1 · verificação: `bun run lint:classes` limpo nos
      arquivos novos (classes Tailwind ordenadas).
- [x] **3. Controller de mostrar/ocultar senha** —
      `frontend/controllers/password_visibility_controller.js` + teste, ligado a
      `<c-ui.field type="password">` — depende de 2 · verificação: `bun run test`.
- [x] **4. Header/nav centralizados nos layouts** — `templates/components/layouts/guest.html`
      ganha header com logo placeholder + toggle de tema; `app.html` ganha o mesmo header
      mais uma sidebar de "configurações de conta" (Segurança, Sessões, Conexões,
      E-mail/Senha) no slot `sidebar` — depende de 2 · verificação: `templates/pages/home.html`
      atualizado para não duplicar mais o toggle, renderiza igual visualmente
      (`python manage.py runserver` + inspeção manual).

      Feito: `templates/layouts/partials/header.html` (logo placeholder + toggle de tema)
      incluído por `guest.html` e `app.html`; `app.html` reorganizado em shell de duas
      colunas (`sidebar` opcional + slot default como `main`, sem mais os slots `header`/
      `main` antigos); `home.html` não duplica mais o toggle. A nav de "configurações de
      conta" propriamente dita (Segurança/Sessões/Conexões/E-mail/Senha) fica para a etapa
      5, que é quem popula o slot `sidebar` de `manage.html`. Verificado com
      `manage.py runserver` + Playwright (`uv run python`, sem `chromium-cli`/dev
      dependency nova): header único, toggle funcional (classe `.dark` + `localStorage`),
      CSS/JS do Vite carregando.
- [x] **5. Override de `allauth/layouts/*.html`** — `base.html`/`entrance.html` estendem
      `<c-layouts.guest>`, `manage.html` estende `<c-layouts.app>` (populando a sidebar) —
      depende de 4 · verificação: `account_login` renderiza dentro do layout `guest`.

      Feito: só `entrance.html` e `manage.html` (nada estende `allauth/layouts/base.html`
      diretamente — ver `grep` no pacote instalado). Os dois usam `{% extends %}` sobre
      `components/layouts/{guest,app}.html` (não a tag Cotton `<c-layouts.*>`, que não
      suporta herança de bloco). Isso exigiu um seam novo em `templates/layouts/base.html`
      (bloco `body` envolvendo `content`) — ver a entrada de risco abaixo sobre por que
      "content" sozinho não bastava. `templates/layouts/partials/manage_nav.html` populada
      via bloco `app_sidebar`; mensagens do Django (`messages`) viram `<c-ui.alert>` por
      `message.tags`. Verificado com `manage.py runserver` (porta 8000, host `localhost`) +
      Playwright: `/auth/login/` (guest) e `/auth/2fa/`, `/auth/sessions/`, `/auth/3rdparty/`,
      `/auth/email/` (app, autenticado via `force_login` + cookie de sessão) renderizam
      header, sidebar com item ativo destacado e o `{% block content %}` de cada página do
      allauth — ainda sem estilo de formulário/botão porque isso é a etapa 6.
- [x] **6. Override de `allauth/elements/*.html`** — cada element delega para o componente
      `ui` correspondente, usando `attrs.tags` do allauth para variante (`prominent`,
      `outline`, `primary`) — depende de 2, 5 · verificação: `account/login.html` (sem
      override próprio) já sai estilizado.

      Feito: os 22 elements do allauth cobertos (`h1`/`h2`/`p`/`hr`/`alert`/`badge`/
      `button`/`button_group`/`form`/`panel`/`field`/`fields`/`table`+`thead`+`tbody`+
      `tr`+`th`+`td`/`provider_list`), mais `provider`/`details`/`img` estilizados direto
      (fora do vocabulário genérico de `apps/ui`, ver ADR 0013). Mapeamento de
      `attrs.tags` → variante/cor centralizado em `apps/ui/templatetags/ui.py`
      (`button_variant`, `button_color`, `tag_color`, `field_attrs`, `field_hide_label`).
      django-cotton não aceita `{% if %}`/`{% elif %}` dentro da lista de atributos de um
      componente nem filtro (`|`) num binding `:attr=`; toda lógica condicional/computada
      virou helper Python + `{% with %}` (ver riscos abaixo). Verificado com
      `manage.py runserver` + Playwright em ~12 páginas (login, signup, password reset,
      email, password change, 2FA index, TOTP activate com QR code, WebAuthn add,
      sessions, connections) — todas estilizadas, sem erro de template. Achado (fora de
      escopo, não corrigido): `account/signup.html` não mostra o campo "Nome"
      (`ACCOUNT_SIGNUP_FIELDS = ["name*", ...]`) mesmo no `form.as_p` puro, sem relação
      com este override — provável gap de configuração do form/model, não da UI.
- [x] **7. Varredura de páginas sem cobertura de elements** — checar cada template em
      `account/`, `mfa/`, `socialaccount/`, `usersessions/` que usa HTML fora dos elements
      (ex.: `usersessions/usersession_list.html`, `mfa/webauthn/authenticator_list.html`,
      `account/email.html`) e decidir override pontual quando necessário — depende de 6 ·
      verificação: inspeção manual de cada URL listada no objetivo (login, signup, logout,
      reset de senha, verificação de e-mail, login por código, MFA index, TOTP, WebAuthn
      add/list, recovery codes, reauthenticate, trust device, sessões, conexões sociais).
      Achados: links crus dentro de `{% blocktranslate %}` (ex. "cadastre-se" no login,
      confirmação de e-mail) não herdavam estilo de `<c-ui.p>`/`help_text` de
      `<c-ui.field>` — corrigido com `[&_a]:text-primary [&_a]:underline
      [&_a]:underline-offset-4 [&_a]:hover:no-underline` em ambos; link "Esqueceu a
      senha?" de `account/password_change.html` é `<a>` cru fora de qualquer element no
      template upstream do allauth — corrigido com override pontual de página envolvendo
      em `{% element button tags="link" %}`. `ACCOUNT_LOGOUT_ON_GET = True` faz logout via
      GET redirecionar direto (sem tela de confirmação) — nada a estilizar aí.
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
  partir de `develop`; este plano; etapa 1 (`apps/ui` registrado, trio de docs, entrada em
  `CONTEXT-MAP.md`); etapa 2 (13 componentes Cotton genéricos em
  `apps/ui/templates/components/ui/`, `bun run lint:classes` estendido para cobrir
  `apps/**/templates` também); etapa 3 (`password_visibility_controller.js` + teste, ligado
  a `<c-ui.field type="password">`).
  etapa 4 (header/toggle de tema centralizado em `templates/layouts/partials/header.html`,
  incluído por `guest.html`/`app.html`); etapa 5 (`allauth/layouts/{entrance,manage}.html`
  sobrescritos, nav de conta em `templates/layouts/partials/manage_nav.html`); etapa 6
  (22 `allauth/elements/*.html` sobrescritos, delegando para `apps/ui` via
  `apps/ui/templatetags/ui.py`); etapa 7 (`<c-ui.p>`/help_text de `<c-ui.field>` ganharam
  estilo de link embutido; `account/password_change.html` ganhou override pontual para o
  link "Esqueceu a senha?"; passagem visual confirmada em login, signup, logout,
  reset/troca de senha, verificação de e-mail, login por código, MFA index/TOTP/WebAuthn,
  reauthenticate, sessões, conexões sociais).
- **Próximo passo**: etapa 8 (i18n / `makemessages`).

## Decisões tomadas no caminho

| Data | Decisão | Motivo | Virou ADR? |
| --- | --- | --- | --- |
| 2026-08-22 | Override de `allauth/elements`+`layouts` em vez de página por página, delegando para `apps/ui` | Estiliza ~80 páginas sobrescrevendo ~15 arquivos; app próprio por exigência do `AGENTS.md` para app novo | [0013](../adr/0013-customizacao-de-ui-do-allauth-via-elements-e-apps-ui.md) |
| 2026-08-22 | JS de WebAuthn/passkey do allauth fica intocado | Superfície de segurança já madura e mantida upstream (ADR 0007) | não |
| 2026-08-22 | Sem HTMX no fluxo de auth | Views do allauth são POST/redirect clássico; forçar swap parcial é briga com a biblioteca | não |
| 2026-08-22 | e2e cobre só telas sem dependência de hardware (nível "a") | Virtual authenticator de WebAuthn via CDP adiciona setup desproporcional ao ganho agora | não |
| 2026-08-22 | `<c-ui.alert severity>`/`<c-ui.badge color>` "success"/"warning" reaproveitam os tokens `secondary`/`tertiary` (não existe token dedicado) | ADR 0012 não previu papel semântico de sucesso/aviso, só M3 genérico; `secondary` (teal) e `tertiary` (amber) já carregam a conotação certa sem token novo | não |
| 2026-08-22 | Variante/cor de `<c-ui.button>`/`<c-ui.badge>`/`<c-ui.alert>` decidida por `attrs.tags` do allauth via helpers Python (`apps/ui/templatetags/ui.py`: `button_variant`, `button_color`, `tag_color`), não `{% if %}` no template | `ElementNode.render` do allauth já parseia `tags="a,b"` em lista antes de expor `attrs.tags` (sem colisão de substring); e django-cotton não aceita `{% if %}`/`{% elif %}` dentro da lista de atributos de um componente (ver risco abaixo) | não |
| 2026-08-22 | `button_variant`: tag `outline`/`link` vence `prominent` quando ambas presentes (`"prominent,login,outline,primary"` → outline) | allauth tagueia ênfase (`prominent` = grande) e estilo visual (`outline` = contornado) como eixos independentes; `<c-ui.button variant>` é um eixo só — o estilo visual explícito é o que importa pra não preencher um botão que o allauth marcou como secundário | não |
| 2026-08-22 | `<c-ui.field hide_label>` some visualmente (`sr-only`) só quando `unlabeled=True` **e** o campo não é checkbox/radio (`field_hide_label` em `ui.py`) | Checkbox/radio não tem `placeholder` como alternativa visual ao rótulo — esconder o label deixaria o campo sem indicação nenhuma do que ele é | não |
| 2026-08-22 | `bun run lint:classes`/`lint:classes:fix` passam a escanear `apps` além de `templates` | Componentes Cotton de app (ex.: `apps/ui/`) não tinham nenhuma checagem de ordenação de classe Tailwind antes disso | não |
| 2026-08-22 | Header (logo + toggle de tema) vive em `templates/layouts/partials/header.html`, incluído por `{% include %}` em `guest.html`/`app.html` — não virou componente Cotton próprio | Bloco pequeno, sem props: `{% include %}` já é o padrão do projeto para "fragmento simples e sem contrato" (`docs/standards/frontend.md`) | não |
| 2026-08-22 | `allauth/layouts/{entrance,manage}.html` usam `{% extends "components/layouts/{guest,app}.html" %}`, não a tag `<c-layouts.*>` | Cotton não suporta herança de bloco Django dentro de um componente — `{% extends %}` sobre o arquivo `.html` do componente funciona porque ele também é um template Django válido | não |
| 2026-08-22 | `templates/layouts/base.html` ganhou um bloco `body` novo envolvendo `content` | Único jeito de `entrance.html`/`manage.html` injetar header/sidebar sem perder para `account/login.html` (que sobrescreve `content` direto) — ver risco abaixo | não |
| 2026-08-22 | Severidade da mensagem do Django (`messages`) mapeada 1:1 para `<c-ui.alert severity>` via `message.tags` (`error`/`warning`/`success`/`info`/`debug`), sem `if`/`elif` | `message.tags` já usa exatamente esses nomes por padrão (`django.contrib.messages`, sem `MESSAGE_TAGS` custom no projeto); `{% if %}/{% elif %}` dentro de atributo de componente Cotton quebra o parser dele (`Invalid block tag ... expected 'endcotton'`) | não |
| 2026-08-22 | `<c-ui.p>` e o `help_text` de `<c-ui.field>` ganham `[&_a]:text-primary [&_a]:underline [&_a]:underline-offset-4 [&_a]:hover:no-underline` fixo na própria classe, não como prop | Links dentro de `{% blocktranslate %}` (ex. "cadastre-se" no login) não passam por nenhum element próprio — só existem como texto interpolado dentro de outro element (`p`); dar estilo ao container via seletor descendente é mais simples que criar um element/component só pra isso | não |
| 2026-08-22 | `templates/account/password_change.html` criado como override pontual de página (não element/layout) | Único lugar do allauth onde um link ("Esqueceu a senha?") é `<a>` cru fora de qualquer `{% element %}` no template upstream — não dá pra alcançar via `elements`/`layouts` sem reescrever a página inteira | não |

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
- `{# comentário #}` do Django só aceita uma linha — comentário de várias linhas nesse
  formato não é removido no render, aparece como texto literal na página (visto em
  `templates/layouts/partials/header.html`, corrigido trocando para
  `{% comment %}...{% endcomment %}`). Cuidado ao anotar os overrides de `elements`/
  `layouts` nas próximas etapas.
- `{% extends %}` precisa ser a primeira tag do arquivo — nem `{% comment %}` antes dele é
  aceito (`must be the first tag`). Comentário de cabeçalho do arquivo vai *depois* do
  `{% extends %}`.
- `bun run dev` serve com CORS restrito a **`http://localhost:8000`** (`vite.config.mjs`),
  não `127.0.0.1:8000` — mesmo servidor, origem diferente para o browser. Testar/screenshot
  manual com qualquer ferramenta (curl não sofre, mas Playwright/browser sim) precisa usar
  exatamente `localhost` na URL, senão os dois `<script type="module">` do Vite falham por
  CORS e a página renderiza sem nenhum CSS/JS — sintoma enganoso, parece bug de template.
- **Bloco Django do mesmo nome usado em mais de um nível do `{% extends %}` não "empilha"**:
  só a versão mais derivada (mais perto da folha) renderiza; qualquer wrapper que um
  ancestral tenha posto around esse bloco é descartado inteiro, não só o conteúdo default.
  Por isso `allauth/layouts/entrance.html`/`manage.html` não podem sobrescrever `content`
  direto (ele já é o nome que `account/login.html` etc. usam) — precisam de um nome de bloco
  próprio e não competido (`guest_content`/`app_content`), com `content` reintroduzido *uma
  única vez*, no nível mais fundo, para o allauth ganhar a resolução. Testado isoladamente
  antes de mexer nos arquivos reais (`render_to_string` num template dir descartável) — vale
  o mesmo teste rápido se essa árvore de blocos crescer mais nas próximas etapas.
- **django-cotton não aceita `{% if %}`/`{% for %}`/`{% with %}` (nenhum block tag) dentro da
  lista de atributos de um componente** (`<c-ui.x {% if %}...{% endif %}>` →
  `TemplateSyntaxError: ... expected 'endcotton'`) — o compilador regex de `<c-x ...>` não
  entende tag aninhada aí. Também **não aceita filtro (`|`) num binding dinâmico
  `:attr="expr"`** (`:attrs="attrs|without_tags"` falha *silenciosamente*: vira
  `UnprocessableDynamicAttr`, o atributo simplesmente não é setado, sem erro nenhum —
  descoberto só ao ver `id=""` no HTML renderizado). Padrão que funciona: computar o valor
  antes, com `{% with x=expr|filtro %}`, e passar `:attr="x"` (variável simples, sem `|`) —
  ou, para o conjunto inteiro de atributos de um `{% element %}` do allauth, mesclar direto
  com `:attrs="attrs"` quando os nomes já batem com os c-vars do componente (evita reescrever
  `{% if attrs.x %}x="{{ attrs.x }}"{% endif %}` por atributo). `apps/ui/templatetags/ui.py`
  (`without_tags`, `field_attrs`) existe por causa dessa restrição.
- **Default de `<c-vars nome="False">` é a *string* `"False"`, não o booleano `False`** —
  `{% if nome %}` dentro do componente é sempre verdadeiro (string não vazia), mesmo sem o
  chamador passar nada. Vale para qualquer c-var pensado como booleano
  (`<c-ui.field hide_label>`, `<c-ui.button_group vertical>`) — declare sem valor
  (`<c-vars ... nome />`, sem `="False"`) para que o padrão vire "variável indefinida" (falsy)
  quando o chamador não passa nada, e `True` de verdade quando passa o atributo puro
  (`<c-x nome>`) ou via `:nome="var_python"`. Bug real, encontrado só depois de renderizar a
  página (rótulo de campo saindo sempre `sr-only`, secreto do TOTP sem rótulo visível) — não
  aparece em `manage.py check` nem em teste de template isolado que não olha o HTML final.

## Fora de escopo

- Dark mode como funcionalidade nova — já vem de graça pelos tokens (ADR 0012); nenhum
  trabalho extra de tema aqui.
- Provedores sociais concretos (Google, GitHub etc.) — `SOCIALACCOUNT_PROVIDERS` continua
  vazio; só o *chrome* das telas de conexão social é estilizado.
- Teste e2e de WebAuthn real (hardware ou virtual authenticator).
- MFA obrigatório para qualquer grupo de usuário — decisão de projeto, não do template
  (ADR 0007).
