# Core — referência para agentes

Interface pública do app, para consultar antes de grepar o código. Vocabulário de
domínio em [`CONTEXT.md`](CONTEXT.md), visão geral humana em [`README.md`](README.md),
convenções de código em [`docs/standards/`](../../docs/standards/).

Atualize esta página no mesmo commit que mudar uma assinatura, adicionar um model ou
remover algo listado aqui.

## Models — `apps.core.models`

- `BaseModel` — abstract base: PK UUID v7 (`UUIDPrimaryKeyMixin`) +
  `created_at`/`updated_at` (`TimestampMixin`). Toda model do projeto deveria herdar
  daqui, direta ou indiretamente.
- `Gender` — `TextChoices`: `MALE`, `FEMALE`, `UNKNOWN` (default). Valueset legal/
  cadastral fixo — não confundir com `SelfRepresentationMixin.gender_identity`.
- `PersonNameMixin` — adiciona `first_name`/`last_name` e a propriedade `.name`
  (`PersonName`); setter `.name = "Full Name"` faz o split.
- `PhoneNumberMixin` — adiciona `phone_number` (string E.164) e a propriedade
  `.phone` (`PhoneNumber`); setter `.phone = "..."` normaliza para E.164.
- `SelfRepresentationMixin` — `social_name`, `gender_identity`, `pronouns`: texto
  livre, todos opcionais.
- `SoftDeleteModel` — campo `deleted_at`; manager `objects` só retorna vivos,
  `all_objects` retorna tudo. Instância ganha `.delete()` (soft), `.restore()`,
  `.hard_delete()`, `.is_deleted`. Queryset ganha `.alive()`/`.dead()`/`.hard_delete()`.
- `SortableMixin` — campo `sort_order` (int, default 0) e `Meta.ordering` por ele.
- `TimestampMixin` — `created_at`/`updated_at` automáticos.
- `UUIDPrimaryKeyMixin` — `id: UUIDField` gerado com `uuid.uuid7`.

## Value objects — `apps.core.domain`

- `PersonName(first, last)` — modelo Pydantic congelado (`frozen=True`).
  `.full`/`.familiar`/`.abbreviated`/`.sorted`/`.initials`/`.mentionable` são
  computed fields; `PersonName.from_full_name("Jason Fried")` faz o parse;
  `.possessive(method="full")` retorna a forma possessiva.
- `PhoneNumber(root)` — `RootModel` Pydantic, valida via `phonenumbers` com a região
  padrão de `config.app_settings`. `.international`/`.national`/`.e164`/
  `.country_code` são computed fields.

## Validators — `apps.core.validators`

- `FileSizeValidator(max_file_size=5*1024*1024)` — validator de Django para tamanho
  máximo de arquivo enviado.
- `get_errors(validation_error) -> list[str]` (`apps.core.services`) — achata as
  mensagens de um `ValidationError` do Django numa lista de strings.

## Presenters — `apps.core.presenters`

- `BasePresenter[T]` — wrapper genérico em torno de um objeto (`self.obj`), delega
  atributos não sobrescritos via `__getattr__`. `BasePresenter.collection(objs)`
  aplica o presenter numa lista. Ponto de extensão: outros apps criam subclasses com
  as propriedades que a apresentação (template/API) precisa e o model não tem.

## Views / URLs — `apps.core.views`, `apps.core.urls` (`app_name="core"`)

- `HomeView` (rota `home`) — página de boas-vindas de exemplo; `build_diagnostics()`
  monta os pares label/valor do painel de diagnóstico (só em `DEBUG`).
- `ping` (rota `ping`) — fragmento HTML de exemplo trocado via HTMX.
- rota `health/` — sondas de prontidão (banco, cache default, cache de sessão,
  storage); rota `health/workers/` — sonda do Celery. Detalhes em
  [`docs/standards/infra.md`](../../docs/standards/infra.md).

## Templatetags — `{% load vite %}` (`apps.core.templatetags.vite`)

- `{% vite_css entry %}`, `{% vite_js entry %}`, `{% vite_asset entry %}` — injetam
  os assets do Vite (dev server em `DEBUG`, manifest de build em produção). `entry` é
  o caminho do input relativo à raiz do projeto (ex.: `frontend/entries/app.js`), a
  mesma chave usada em `vite.config.mjs`.

## Tasks — `apps.core.tasks` (Celery, autodiscover)

- `echo(mensagem: str) -> str` (task `core.echo`) — task de exemplo, só loga e
  retorna a mensagem; troque pela primeira task real do projeto.

## Management commands

- `makemessages` / `compilemessages` (`apps/core/management/commands/`) — wrappers
  que aplicam `settings.LANGUAGES` por padrão e ignoram `.venv`/`node_modules`;
  detalhes em [`docs/standards/i18n.md`](../../docs/standards/i18n.md).

## Admin

- Nenhum model registrado (`apps/core/admin.py` está vazio — todos os models daqui
  são abstratos).
