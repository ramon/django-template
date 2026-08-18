# 0007. Autenticação com django-allauth, MFA e CORS liberado para a API

- **Status**: Aceito
- **Data**: 2026-08-18
- **Relacionados**: `docs/standards/auth.md`

## Contexto

Um projeto novo precisa de cadastro, login, verificação de e-mail, recuperação de senha e,
mais cedo ou mais tarde, segundo fator — construir isso à mão significa reimplementar fluxo
de segurança (tokens de confirmação, expiração, hashing) que já tem solução madura e
mantida. O modelo de usuário também precisa caber no resto do projeto: `apps/accounts.User`
usa e-mail como identificador, não username, e ganha `Profile` associado na criação (ver
`apps/accounts/models/user.py`).

Ao mesmo tempo, a API (`django-ninja`) exige autenticação global — nenhum endpoint responde
como anônimo — e pode vir a ser chamada por uma origem diferente da que serve o HTML (um
app mobile, um front separado no futuro), o que exige uma política de CORS explícita em vez
de depender do mesmo-origin que o server-rendered HTML garante de graça.

## Decisão

Autenticação é `django-allauth`, com os extras `mfa` e `socialaccount`
(`config/settings/parts/auth.py`):

- **Login por e-mail**, sem username: `ACCOUNT_LOGIN_METHODS = {"email"}` e
  `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`, casando com `AUTH_USER_MODEL = "accounts.User"`.
- **Verificação de e-mail obrigatória** (`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`): conta
  nova não loga sem confirmar. Confirmação e login por código aceitam o link clicado direto
  (`ACCOUNT_CONFIRM_EMAIL_ON_GET`, `ACCOUNT_LOGIN_BY_CODE_ENABLED`).
- **MFA com três fatores**: TOTP, WebAuthn (com passkey como método de login,
  `MFA_PASSKEY_LOGIN_ENABLED`) e recovery codes. Opcional por usuário — nada força o
  cadastro a configurar segundo fator.
- **Sessões rastreadas** via `allauth.usersessions`, o que também habilita "sair de todos os
  dispositivos" sem código adicional.
- **Contas sociais** ficam com a lista de provedores vazia (`SOCIALACCOUNT_PROVIDERS = {}`):
  a dependência já está instalada e configurada, mas nenhum provedor concreto é uma decisão
  de projeto, não do template.
- **Senha**: `Argon2PasswordHasher` como único hasher e os quatro validadores padrão do
  Django, com `MinimumLengthValidator` configurável por `MIN_PASSWORD_LENGTH` (padrão 8).
- Rotas inteiras vêm de `allauth.urls`, montadas em `auth/` (`config/urls/web.py`) —
  `apps/accounts/views.py` e `urls.py` ficam vazios de propósito: o app é dono do model
  (`User`, `Profile`) e da API de perfil, não da UI de autenticação.

CORS é liberado a partir do princípio de que a API pode ter consumidor fora da origem que
serve o HTML (`config/settings/parts/cors.py`): `CORS_ALLOW_ALL_ORIGINS = DEBUG` — em
desenvolvimento qualquer origem passa, sem fricção para testar um client externo — e fora de
`DEBUG` a lista vem de `CORS_ALLOWED_ORIGINS` no ambiente, vazia por padrão (nada passa até
alguém declarar uma origem).

## Consequências

- **Positivas**: fluxo de conta inteiro (cadastro, verificação, recuperação de senha, MFA,
  sessões) vem testado e mantido por terceiro, em vez de reimplementado; adicionar um
  provedor social é configuração (`SOCIALACCOUNT_PROVIDERS`), não código novo; CORS fechado
  por padrão em produção não bloqueia teste manual em desenvolvimento.
- **Negativas**: UI de autenticação é a do allauth (templates próprios, não os do projeto)
  até alguém decidir customizá-la; verificação de e-mail mandatória exige backend de e-mail
  funcional mesmo em ambientes de teste manual — em desenvolvimento isso é absorvido pelo
  backend de console (`config/settings/development.py`); esquecer de popular
  `CORS_ALLOWED_ORIGINS` em produção quebra silenciosamente qualquer client externo, sem
  aviso no boot.
- **Neutras**: `AUTHENTICATION_BACKENDS` lista o backend do Django antes do do allauth —
  ordem que o allauth exige e que não deve ser invertida.

## Alternativas consideradas

### Autenticação própria (`django.contrib.auth` puro + views escritas à mão)

Menos dependência, mas reimplementa confirmação de e-mail, recuperação de senha e segundo
fator — superfície de segurança que o allauth já cobre e mantém contra CVE.

### MFA obrigatório para todo usuário

Mais seguro por padrão, mas eleva a fricção de cadastro de qualquer projeto gerado a partir
do template, inclusive os que não lidam com dado sensível. Fica como decisão de cada
projeto — o suporte já está instalado, falta só exigir.

### `CORS_ALLOWED_ORIGINS` com uma origem coringa em produção

Mais simples de configurar, mas abre a API para qualquer site fazer requisição
autenticada por cookie de sessão — a lista explícita é o preço de manter CSRF e sessão como
mecanismo de auth também para a API.
