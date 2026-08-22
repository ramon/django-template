# Accounts — referência para agentes

Interface pública do app, para consultar antes de grepar o código. Vocabulário de
domínio em [`CONTEXT.md`](CONTEXT.md), visão geral humana em [`README.md`](README.md).

Atualize esta página no mesmo commit que mudar uma assinatura, adicionar um model ou
remover algo listado aqui.

## Models — `apps.accounts.models`

- `User(PermissionsMixin, PersonNameMixin, PhoneNumberMixin, BaseModel, AbstractBaseUser)`
  — é o `AUTH_USER_MODEL`. `USERNAME_FIELD = "email"`;
  `REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]`.
  `UserManager.create_user(email, password=None, **extra_fields)` normaliza o e-mail,
  salva o `User` e cria o `Profile` associado automaticamente — não crie um `Profile`
  à parte. `UserManager.create_superuser(email, password=None, **extra_fields)` seta
  `is_staff`/`is_superuser`.
- `Profile(AvatarMixin, DocumentMixin, PhoneNumberMixin, SelfRepresentationMixin,
  BaseModel)` — one-to-one com `User` (`related_name="profile"`). Campos:
  `nationality`/`document_type`/`document` (ver `DocumentMixin`), `birth_date`,
  `gender` (`apps.core.models.Gender`, default `UNKNOWN`). `ProfileManager` já
  aplica `select_related("user")` no manager padrão.
- `AvatarMixin` (`apps.accounts.models.mixins`) — campo `avatar` (`ImageField`,
  valida extensão `jpg/jpeg/png/webp` e tamanho ≤5MB via `FileSizeValidator` de
  `apps.core`). `.avatar_url()` retorna a URL da imagem enviada ou, se não houver,
  string vazia — sem fallback para serviço de terceiro
  ([ADR 0014](../../docs/adr/0014-remover-fallback-de-avatar-para-o-gravatar.md)).
- `DocumentMixin` (`apps.accounts.models.mixins`) — campos `nationality`
  (`django_countries.fields.CountryField`, opcional), `document_type`
  (`apps.accounts.models.choices.DocumentType`: `CPF`/`SSN`/`PASSPORT`, nunca
  setado à mão) e `document` (`CharField`, único, normalizado sem pontuação).
  `.clean()` é um no-op sem `nationality`; com ela preenchida, exige `document` e
  usa `apps.accounts.domain.Document` para validar e normalizar de acordo com o
  tipo derivado (`BR`→CPF, `US`→SSN, qualquer outra→passaporte sem validação de
  formato) — levanta `django.core.exceptions.ValidationError` se inválido. Passa
  `allow_repeated_digits=settings.DEBUG` ao `Document`: um CPF de dígito único
  repetido (`111.111.111-11`) só é aceito com `DEBUG=True`. Ver
  [ADR 0010](../../docs/adr/0010-documento-de-identidade-tipado-pela-nacionalidade.md).

## Domain — `apps.accounts.domain`

- `Document(BaseModel)` (Pydantic, `apps.accounts.domain.value_objects.document`)
  — recebe `nationality` (código ISO alpha-2), `value` (número bruto) e
  `allow_repeated_digits: bool = False`. Valida e normaliza no construtor via
  `python-stdnum` para `BR`/`US`; para as demais nacionalidades, só exige um
  caractere alfanumérico. `.document_type` (`"cpf"`, `"ssn"` ou `"passport"`) é
  derivado de `nationality`. Levanta `pydantic.ValidationError` se o número não
  for válido para o tipo — inclui CPF de dígito repetido, a menos que
  `allow_repeated_digits=True`.
- `calculate_age(birth_date: date | datetime) -> int` (`apps.accounts.domain.services`)
  — idade em anos completos na data de hoje.

## Presenters — `apps.accounts.presenters`

- `UserPresenter(BasePresenter[User])` — sem propriedades extras hoje; ponto de
  extensão para apresentação de `User`.
- `ProfilePresenter(BasePresenter[Profile])` — `.name`, `.first_name()`,
  `.last_name()`, `.email()` (todos via `obj.user`), `.age` (via
  `calculate_age(obj.birth_date)`, `None` se `birth_date` não estiver preenchida).

## API — `apps.accounts.api` (router montado em `/profile/`)

- `GET /profile/me` → `UserInfoOut` (`sub`, `name`, `given_name`, `family_name`,
  `picture`, `email` — schema no formato userinfo do OIDC). Implementação em
  `apps.accounts.api.endpoints.profile.profile_me`; devolve
  `ProfilePresenter(request.user.profile)`. Autenticação já é garantida globalmente
  pela `NinjaAPI` — dentro do endpoint `request.user` nunca é anônimo.

## Admin — `apps.accounts.admin`

- `UserAdmin` — `list_display`: name, email, is_active, is_staff, is_superuser.
- `ProfileAdmin` — `list_display`: user, gender, created_at; `list_filter`: gender.

## Forms — `apps.accounts.forms`

- `SignupForm(allauth.account.forms.SignupForm)` — registrado via `ACCOUNT_FORMS`
  (`config/settings/parts/auth.py`), é o form real que `/auth/signup/` usa. Acrescenta o
  campo `name` (nome completo, texto livre) e, em `clean_name()`, quebra em
  `first_name`/`last_name` via `PersonName.from_full_name` (`apps.core.domain`) —
  levanta `ValidationError` se não houver um espaço separando nome e sobrenome. Não
  precisa de `ACCOUNT_ADAPTER`: `DefaultAccountAdapter.save_user()` do próprio allauth já
  lê `first_name`/`last_name` de `form.cleaned_data` sozinho.

## Views / URLs

- `apps/accounts/views.py` e `apps/accounts/urls.py` estão vazios — o app hoje só
  expõe API, sem páginas server-rendered próprias. `apps/accounts/forms.py` é a exceção
  legítima: o allauth descobre form customizado por `ACCOUNT_FORMS`, não por view/URL
  própria do app.
