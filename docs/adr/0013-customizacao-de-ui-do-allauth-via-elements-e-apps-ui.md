# 0013. Customização de UI do allauth via override de elements/layouts, delegando para `apps/ui`

- **Status**: Aceito
- **Data**: 2026-08-22
- **Relacionados**: [0006](0006-django-cotton-para-componentes-de-template.md),
  [0007](0007-autenticacao-com-django-allauth-e-mfa.md),
  [0012](0012-tema-com-tokens-no-molde-do-material-design-3.md),
  `docs/standards/frontend.md`

## Contexto

A UI de autenticação vem 100% dos templates padrão do `django-allauth` — a ADR 0007 já
registrava isso como consequência negativa aceita, a resolver quando alguém decidisse
customizá-la. O allauth moderno (65.x) não espera que cada página seja reescrita: toda
página de conta (`account/login.html`, `mfa/index.html`, `usersessions/usersession_list.html`
etc.) já é montada com `{% element %}` em vez de HTML cru — botão, campo, formulário, painel,
alerta e título passam por `allauth/elements/*.html`, e cada página estende
`allauth/layouts/{base,entrance,manage}.html`. É o ponto de extensão oficial da biblioteca
para plugar um design system: sobrescrever os ~15 arquivos de `elements`/`layouts` estiliza
as ~80 páginas de uma vez, sem tocar nelas.

O projeto, por outro lado, já tem tokens de tema (ADR 0012, molde Material Design 3, claro e
escuro) e componentes Cotton (ADR 0006), mas nenhum componente genérico de UI ainda —
`templates/components/layouts/{guest,app}.html` existem como esqueleto vazio, e o único
vocabulário visual concreto é o de `templates/pages/home.html` (card, botão, pill, chip de
código), usado ad-hoc, sem componente por trás.

## Decisão

Sobrescrevemos `allauth/elements/*.html` e `allauth/layouts/*.html` — não cada página
individual — delegando a marcação para uma biblioteca nova de componentes Cotton genéricos
(`<c-ui.button>`, `<c-ui.field>`, `<c-ui.panel>`, `<c-ui.alert>`, `<c-ui.form>`...), que segue
o vocabulário visual já estabelecido por `home.html` sobre os tokens da ADR 0012.

Essa biblioteca mora em `apps/ui/`, um app Django próprio sem lógica de domínio:
`apps/ui/templates/components/ui/*.html` — descoberto pelo `cotton_loader` do django-cotton,
que varre `apps.get_app_configs()` independente do `APP_DIRS = False` do projeto
(`config/settings/parts/templates.py`). Por ser um app novo, carrega o trio de documentação
do `AGENTS.md` (`CONTEXT.md` com o vocabulário dos próprios componentes — variante de botão,
severidade de alerta, papel de superfície —, `README.md`, `AGENTS.md`), e entra em
`CONTEXT-MAP.md`.

`allauth/layouts/entrance.html` (login, signup, reset de senha, verificação de e-mail, login
por código) passa a estender `<c-layouts.guest>`; `allauth/layouts/manage.html` (MFA, sessões,
conexões sociais, troca de e-mail/senha) passa a estender `<c-layouts.app>` — primeiro uso
real do slot `sidebar` desse layout, com uma navegação de configurações de conta. Os dois
layouts ganham um header centralizado (antes duplicado em `home.html`) com o toggle de tema
já existente (`theme_controller.js`, ADR 0012).

O JS de WebAuthn/passkey do próprio allauth (`mfa/js/webauthn.js`, `webauthn-json.js`,
`account/js/onload.js`) permanece intocado — só os elementos ao redor (botões, formulários)
são estilizados.

## Consequências

- **Positivas**: qualquer tela nova do allauth (ou um provedor social futuro) herda o estilo
  de graça, sem exigir override de página; os componentes de `apps/ui/` ficam disponíveis
  para qualquer página do projeto, não só as de auth; superfície de manutenção menor (~15
  arquivos de `elements`/`layouts` contra ~80 páginas).
- **Negativas**: uma tela do allauth com layout muito específico, não coberto pelos
  `elements` padrão, ainda vai exigir override de página individual; mudar uma cor ou
  espaçamento simples atravessa três camadas (element do allauth → componente `ui` → token
  de tema) em vez de uma edição direta na página.
- **Neutras**: `apps/ui` não tem models nem migrations — existe só pela descoberta de
  template do `cotton_loader` e pela exigência de documentação por app do `AGENTS.md`; os
  controllers Stimulus ligados aos componentes (ex.: mostrar/ocultar senha) continuam em
  `frontend/controllers/`, que não é organizado por app.

## Alternativas consideradas

### Sobrescrever cada página do allauth individualmente

Mais controle por tela, mas duplica marcação de botão/campo/painel em ~80 arquivos — mudar o
tema ou corrigir um componente exige caçar cada ocorrência, o mesmo problema que a ADR 0012
resolveu para cor.

### Componentes genéricos em `templates/components/ui/`, sem app próprio

Mais simples — sem `AppConfig`, sem o trio de documentação. Mas deixa o vocabulário de
componentes fora do inventário de `apps/` do projeto, sem lugar formal para crescer (por
exemplo, um helper Python de renderização de formulário no futuro).

### Reimplementar WebAuthn/passkey com Stimulus, no padrão do resto do projeto

Alinha 100% com a convenção de frontend, mas reimplementa superfície de segurança madura e
mantida upstream pelo allauth — contraria o motivo original da ADR 0007 de não reinventar
esse fluxo.
