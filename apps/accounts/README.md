# Accounts

Identidade do usuário: autenticação (`User`) e o perfil pessoal que a estende
(`Profile`) — documento, data de nascimento, gênero e avatar.

Para o vocabulário do domínio (o que é `User`, `Profile`, `Document`, `Avatar`...),
veja [`CONTEXT.md`](CONTEXT.md).

## O que tem aqui

- **`User`**: model de autenticação, com e-mail como username. Nome completo e
  telefone são obrigatórios já na criação. Ao criar um `User`, um `Profile` vazio é
  criado junto — os dois nascem sempre juntos.
- **`Profile`**: dados complementares que não fazem parte da autenticação —
  documento, data de nascimento, gênero, avatar, e como a pessoa se autorrepresenta
  (nome social, identidade de gênero, pronomes — herdado de `apps.core`).
- **Avatar com fallback pro Gravatar**: se o usuário não enviou uma imagem, a UI usa
  uma gerada a partir do hash do e-mail pelo serviço externo Gravatar.
- **API** (`django-ninja`, montada em `/profile/`): `GET /profile/me` devolve os
  dados do usuário autenticado num formato parecido com o userinfo do OIDC.

## Para quem for mexer aqui

Referência da interface pública (models, funções, endpoints, com assinatura) fica em
[`AGENTS.md`](AGENTS.md). Convenções de código — camadas, testes, tipagem — ficam em
[`docs/standards/backend.md`](../../docs/standards/backend.md).
