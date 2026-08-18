# 0008. Desativar o envio de PII para o Sentry

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: 0007, `docs/standards/observability.md`

## Contexto

O SDK do Sentry oferece `send_default_pii`, que, ligado, anexa a cada evento o que
conseguir capturar da requisição: IP do usuário, cookies, headers como `Authorization`, e —
quando o `DjangoIntegration` reconhece o usuário autenticado — nome e e-mail do
`request.user`. É a opção mais rica para depurar um erro em produção, mas o custo é enviar
dado pessoal para um serviço de terceiro a cada exceção, sem filtro.

Este projeto usa e-mail como identidade (`AUTH_USER_MODEL = "accounts.User"`, login por
e-mail via allauth — [ADR 0007](0007-autenticacao-com-django-allauth-e-mfa.md)) e tem MFA e
verificação de conta no caminho crítico de autenticação. Um erro nesse caminho é exatamente
o tipo de evento mais provável de carregar e-mail, IP e cabeçalho de sessão do usuário — e
também o mais sensível de vazar para uma conta de terceiro no Sentry. Manter
`send_default_pii=True` estava em desacordo com o princípio de minimização de dado que o
projeto quer seguir por padrão, especialmente relevante para um template usado por projetos
sujeitos à LGPD.

## Decisão

`send_default_pii=False` em `config/settings/parts/sentry.py`. O evento enviado ao Sentry
continua com stack trace, request path, método HTTP e o `correlation_id` do `django-guid`
(que já é a chave usada para cruzar um erro com o log estruturado, sem precisar de e-mail ou
IP) — só o que identifica a pessoa por trás da requisição fica de fora.

Investigar um erro específico continua possível: o `correlation_id` do evento no Sentry é o
mesmo que aparece no header `X-Correlation-Id` e no log em JSON do `structlog`, e é por ali
que se busca o contexto completo daquela requisição, já dentro do perímetro de log do
próprio projeto, não do Sentry.

## Consequências

- **Positivas**: nenhum e-mail, IP ou cookie de sessão sai do projeto por padrão via Sentry;
  reduz superfície de exposição em caso de incidente na própria conta do Sentry;
  projetos gerados a partir do template herdam a opção mais conservadora sem precisar
  lembrar de desligá-la.
- **Negativas**: o evento no Sentry sozinho não diz "qual usuário" bateu no erro — é preciso
  cruzar com o log via `correlation_id` para isso. Times acostumados a abrir o evento e ver
  o e-mail direto precisam desse passo extra.
- **Neutras**: `traces_sample_rate` e `profile_session_sample_rate` (ambos 0.1) não mudam —
  a decisão é só sobre PII, não sobre volume de captura.

## Alternativas consideradas

### Manter `send_default_pii=True` e usar `before_send` para filtrar

Dá controle fino (mandar IP mas não e-mail, por exemplo), mas exige manter uma função de
scrubbing em dia com o que o SDK decide capturar em cada versão — mais superfície para
errar por omissão. Desligar a opção na origem é a via mais simples de auditar: não há dado
para vazar por um filtro que ficou desatualizado.

### `send_default_pii=False` só em produção, `True` em desenvolvimento

O Sentry só é inicializado fora de `DEBUG` (ver `config/settings/parts/sentry.py`), então
não há ambiente de desenvolvimento em que a opção esteja ativa para diferenciar — a
distinção não se aplicaria a nada.
