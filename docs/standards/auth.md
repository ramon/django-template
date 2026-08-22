# Padrões: autenticação, autorização e CORS

Como conta, login e acesso à API funcionam neste projeto. Comandos e stack no
[`README.md`](../../README.md); o porquê da escolha do allauth, do MFA e do CORS liberado
para a API está no [ADR 0007](../adr/0007-autenticacao-com-django-allauth-e-mfa.md).

## Identidade

`AUTH_USER_MODEL = "accounts.User"`. Login é por **e-mail**, sem username
(`ACCOUNT_LOGIN_METHODS = {"email"}`, `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`). Criar um
usuário passa pelo manager, nunca por `User.objects.create()`:

```python
User.objects.create_user(email="a@example.com", password="...")
```

`create_user` (`apps/accounts/models/user.py`) faz o hash da senha e cria o `Profile`
associado — é por isso que `UserFactory` (`apps/accounts/tests/factories.py`) também passa
pelo manager em vez do `objects.create` padrão do factory_boy. Ver
[`testing.md`](testing.md#fixtures-e-factories).

## Senha

- Hasher único: `Argon2PasswordHasher`.
- Validadores padrão do Django, com `MinimumLengthValidator` configurável por
  `MIN_PASSWORD_LENGTH` (`.env`, padrão 8).

Variável nova de política de senha é campo em `AUTH_PASSWORD_VALIDATORS`
(`config/settings/parts/auth.py`), não checagem manual em view.

## Fluxo de conta: quem é dono do quê

Toda a UI de autenticação (login, cadastro, confirmação de e-mail, recuperação de senha,
MFA) vem de `django-allauth`, montada em `auth/` (`config/urls/web.py`,
`include("allauth.urls")`). Por isso `apps/accounts/views.py` e `apps/accounts/urls.py`
estão vazios de propósito — o app é dono do **model** (`User`, `Profile`) e da **API de
perfil** (`apps/accounts/api/`), não da UI de login. Customizar uma tela de auth é
sobrescrever o template do allauth (`allauth/account/...` no
[template lookup](https://docs.allauth.org/en/latest/common/templates.html)), não recriar a
view — mas já vem estilizada: o tema (ADR 0012) chega em toda tela via override de
`allauth/elements/`/`allauth/layouts/`, delegando para os componentes Cotton genéricos de
`apps/ui/` (ADR 0013). Ver [`frontend.md#telas-do-allauth-sobrescreva-elementslayouts-não-a-página`](frontend.md).

### Verificação de e-mail: obrigatória

`ACCOUNT_EMAIL_VERIFICATION = "mandatory"` — conta nova não loga até confirmar o e-mail.
`ACCOUNT_CONFIRM_EMAIL_ON_GET` e `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED` aceitam a
confirmação pelo link clicado direto, sem POST intermediário.

Consequência prática: testar cadastro manualmente exige um backend de e-mail que responda.
Em desenvolvimento é o backend de console (`config/settings/development.py`) — o e-mail
"enviado" aparece no terminal do `runserver`; em produção, as variáveis `EMAIL_*` do
`.env.example`.

### Login por código

`ACCOUNT_LOGIN_BY_CODE_ENABLED` e `ACCOUNT_LOGIN_BY_CODE_TRUST_ENABLED` habilitam login sem
senha, por código enviado ao e-mail. `ACCOUNT_LOGOUT_ON_GET` faz o logout responder a GET —
não é um detalhe de segurança a "corrigir" para POST; é a configuração deste projeto.

## MFA

Três fatores suportados (`MFA_SUPPORTED_TYPES`): **TOTP**, **WebAuthn** (com passkey
utilizável como método de login, `MFA_PASSKEY_LOGIN_ENABLED`) e **recovery codes**.
`MFA_TRUST_ENABLED` permite marcar um dispositivo como confiável e pular o segundo fator
nele por um tempo.

MFA é **opcional por usuário** — nada no código força o cadastro a configurá-lo. Exigir MFA
para todo usuário (ou para um grupo, como staff) é decisão de cada projeto gerado a partir
do template, não algo a inferir daqui; se for tomada, registre um ADR novo.

## Sessões

`allauth.usersessions` rastreia sessão por dispositivo (`USERSESSIONS_TRACK_ACTIVITY`), o
que inclui "sair de todos os dispositivos" pronto, sem código adicional. O middleware
correspondente (`UserSessionsMiddleware`) já está na lista, depois do
`AccountMiddleware`.

## Contas sociais

`SOCIALACCOUNT_PROVIDERS` está vazio de propósito (`config/settings/parts/auth.py`) — a
dependência (`django-allauth[socialaccount]`) já está instalada, mas nenhum provedor
concreto é decisão do template. Adicionar um provedor é configuração, não código novo:
declare o provedor no dicionário, com client id/secret vindo de
`IntegrationSettings` (`config/app_settings/integration.py`), nunca hardcoded.

## API: autenticação sempre, CORS por origem

A `NinjaAPI` (`apps/*/api/router.py`) exige `django_auth` globalmente — nenhum endpoint
responde como anônimo, e `request.user` nunca é `AnonymousUser` dentro de um endpoint. Ver
[`backend.md#api-django-ninja`](backend.md#api-django-ninja).

CORS (`django-cors-headers`, `config/settings/parts/cors.py`) existe para essa mesma API
poder ser chamada de uma origem diferente da que serve o HTML — um client mobile, um front
separado no futuro:

```python
CORS_ALLOW_ALL_ORIGINS = DEBUG        # em dev, qualquer origem passa
CORS_ALLOWED_ORIGINS = [...]          # fora de DEBUG, lista explícita do .env
```

`CORS_ALLOWED_ORIGINS` (`.env`) é vazio por padrão — **nada passa em produção até alguém
declarar uma origem**, esquema e porta incluídos
(`https://app.exemplo.com,https://admin.exemplo.com`). Não amplie para um coringa em
produção: a API usa sessão/cookie como credencial, e uma origem coringa com CORS aberto
permitiria requisição autenticada de qualquer site.

## Checklist

- [ ] usuário criado via `create_user`/`UserFactory`, nunca `objects.create()`
- [ ] tela de auth nova é override de template do allauth, não view própria em
      `apps/accounts/`
- [ ] provedor social novo: credenciais em `IntegrationSettings`, não no dicionário direto
- [ ] origem nova de front/consumidor de API: `CORS_ALLOWED_ORIGINS` no `.env` de produção,
      nunca coringa
