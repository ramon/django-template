# Plano: corrigir o cadastro (HTTP 500 por falta de nome)

- **Status**: Em andamento
- **Início**: 2026-08-22
- **Última atualização**: 2026-08-22
- **Relacionados**: `docs/plans/frontend-auth-styling.md` (etapa 9, onde o bug foi achado),
  ADR [0007](../adr/0007-autenticacao-com-django-allauth-e-mfa.md)

## Objetivo

`/auth/signup/` cadastra um usuário de verdade (com `first_name`/`last_name`
preenchidos), sem HTTP 500, coletando o nome no próprio formulário.

## Contexto

`ACCOUNT_SIGNUP_FIELDS = ["name*", "email*", "password1*", "password2*"]`
(`config/settings/parts/auth.py:47`) declara um campo `"name"` obrigatório, mas o
`BaseSignupForm` do allauth (`allauth/account/forms.py:276-334`) só sabe montar campo pra
`email`, `email2`, `username` e `phone` — `"name"` é lido da configuração e ignorado. Por
isso a tela de cadastro nunca mostra campo de nome nenhum (confirmado via `curl`: só
`email`, `password1`, `password2`).

`User` (`PersonNameMixin`, `apps/accounts/models/user.py`) exige `first_name`/`last_name`
— `CharField` sem `blank=True`. Como `BaseModel.save()` roda `full_clean()` automático
(ADR 0011), salvar sem esses campos derruba `ValidationError` não tratada → 500.

**Achado que simplifica a correção**: `DefaultAccountAdapter.save_user()`
(`allauth/account/adapter.py:345-388`) já procura `first_name`/`last_name` em
`form.cleaned_data` e chama `user_field(user, "first_name", ...)` sozinho — não precisa de
`ACCOUNT_ADAPTER` customizado, nem do property setter `User.name` (`PersonNameMixin`, que
quebra "Nome Completo" em first/last). Só falta o **form** ter esses campos — o resto do
pipeline (`save_user` → `user.save()` → `full_clean()`) já funciona.

`apps/accounts/forms.py` não existe ainda; `views.py`/`urls.py` estão vazios de propósito
(a UI é do allauth, ver `docs/standards/auth.md`) — um form de signup é a primeira exceção
legítima a isso, porque o allauth também busca form customizado via `ACCOUNT_FORMS`.

## Etapas

- [ ] **1. `apps/accounts/forms.py::SignupForm`** — subclasse de
      `allauth.account.forms.SignupForm`, adiciona o(s) campo(s) de nome (ver pergunta em
      aberto) · verificação: teste unitário do form isolado (cria form com dados válidos,
      `is_valid()` verdadeiro, `cleaned_data` tem `first_name`/`last_name`).
- [ ] **2. Registrar `ACCOUNT_FORMS`** — `config/settings/parts/auth.py`:
      `ACCOUNT_FORMS = {"signup": "apps.accounts.forms.SignupForm"}` — depende de 1 ·
      verificação: `manage.py shell` resolve o form certo via
      `allauth.account.forms.SignupForm` (o de `apps.accounts`, não o padrão).
- [ ] **3. Teste de integração do fluxo real** — `apps/accounts/tests/integration/` ou
      `tests/e2e/test_auth_signup.py`: POST em `/auth/signup/` com nome preenchido cria
      `User` com `first_name`/`last_name` certos, sem 500 — depende de 2 · verificação:
      `uv run pytest` novo teste passa.
- [ ] **4. Reativar a cobertura e2e completa de signup** — `tests/e2e/test_auth_signup.py`
      hoje só testa renderização (comentário no arquivo aponta pra este bug); acrescentar
      o teste de cadastro bem-sucedido, removendo a ressalva — depende de 3 · verificação:
      `bun run build && uv run pytest -m e2e` passa.
- [ ] **5. Docs** — `apps/accounts/AGENTS.md` ganha a entrada do `SignupForm` novo;
      `docs/plans/frontend-auth-styling.md` marca o achado da etapa 9 como resolvido, com
      link pra este plano — depende de 4 · verificação: revisão de texto.
- [ ] **6. Fechamento** — checklist de `docs/standards/quality-gates.md` completo, PR pra
      `develop` (só com autorização explícita).

## Estado atual

- **Feito**: branch `fix/accounts-cadastro-sem-nome` criada a partir de `develop`; este
  plano.
- **Em andamento**: etapa 1.
- **Próximo passo**: decidir a pergunta em aberto abaixo, depois escrever o `SignupForm`.

## Decisões tomadas no caminho

| Data | Decisão | Motivo | Virou ADR? |
| --- | --- | --- | --- |
| 2026-08-22 | Sem `ACCOUNT_ADAPTER` customizado — só `SignupForm` | `DefaultAccountAdapter.save_user()` já lê `first_name`/`last_name` de `form.cleaned_data` sozinho; adapter novo seria código morto | não |

## Riscos e pontos de atenção

- `ACCOUNT_SIGNUP_FIELDS` continua dizendo `"name*"`, mas essa chave nunca fez nada — vale
  considerar removê-la da lista pra não sugerir um comportamento que não existe (ou
  documentar por que fica).
- `docs/standards/auth.md` diz que `apps/accounts/views.py`/`urls.py` ficam vazios "de
  propósito" porque a UI é do allauth — o `forms.py` novo não contraria isso (o allauth
  também descobre form por `ACCOUNT_FORMS`), mas vale uma frase no padrão pra deixar
  explícito que forms de allauth são exceção legítima.

## Fora de escopo

- Qualquer outro gap de `ACCOUNT_SIGNUP_FIELDS`/model (este plano resolve só o campo de
  nome).
- Mudar a UI/estilo do campo novo — já herda estilo de `apps/ui` via
  `allauth/elements/fields.html` (ver `docs/plans/frontend-auth-styling.md`), sem trabalho
  extra.

## Pergunta em aberto

Campo único "Nome completo" (quebrado em `first_name`/`last_name` via o setter que já
existe, `PersonNameMixin.name`) ou dois campos separados "Nome"/"Sobrenome" (batem direto
com o que `save_user` já procura, sem usar o setter)? Ambos resolvem o bug — é decisão de
UX do formulário de cadastro, não técnica.
