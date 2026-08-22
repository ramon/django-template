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
- `Profile(AvatarMixin, PhoneNumberMixin, SelfRepresentationMixin, BaseModel)` — one-
  to-one com `User` (`related_name="profile"`). Campos: `document` (11 caracteres,
  único, sem validação de dígito), `birth_date`, `gender`
  (`apps.core.models.Gender`, default `UNKNOWN`). `ProfileManager` já aplica
  `select_related("user")` no manager padrão. A propriedade `.email` delega para
  `user.email` — é o contrato exigido por `AvatarMixin` para montar o fallback do
  Gravatar.
- `AvatarMixin` (`apps.accounts.models.mixins`) — campo `avatar` (`ImageField`,
  valida extensão `jpg/jpeg/png/webp` e tamanho ≤5MB via `FileSizeValidator` de
  `apps.core`). `.avatar_url()` retorna a URL da imagem enviada ou, se não houver,
  chama `gravatar_url(self.email)`.

## Domain services — `apps.accounts.domain.services`

- `calculate_age(birth_date: date | datetime) -> int` — idade em anos completos na
  data de hoje.

## Services — `apps.accounts.services`

- `gravatar_url(email: str, size: int = 40) -> str` — monta a URL do Gravatar a
  partir do hash SHA-256 do e-mail (minúsculo).
- `get_avatar_from_url(url: str) -> File` — baixa uma imagem de uma URL externa para
  um arquivo temporário, pronto para atribuir a um `ImageField`.

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

## Views / URLs

- `apps/accounts/views.py` e `apps/accounts/urls.py` estão vazios — o app hoje só
  expõe API, sem páginas server-rendered próprias.
