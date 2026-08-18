# Padrões: backend

Como o código Python deste projeto é organizado. Para stack, instalação e comandos, veja
o [`README.md`](../../README.md).

## Anatomia de um app

Um app é um contexto de domínio, não uma camada técnica. Ele vive em `apps/<dominio>/` e
usa só os módulos de que precisa — nada de criar arquivo vazio para "completar" a
estrutura:

```text
apps/accounts/
├── models/              # persistência (pacote quando há mais de um model)
├── domain/              # regra de negócio pura, sem Django
│   ├── services.py
│   └── value_objects/
├── services/            # integrações e efeitos colaterais (ex.: gravatar.py)
├── api/                 # django-ninja: router, schemas, endpoints/
├── presenters.py        # adapta model → apresentação (HTML ou API)
├── views.py             # views web
├── urls.py              # rotas do app, com app_name
├── admin.py
├── tasks.py             # descoberto pelo autodiscover do Celery
├── locale/              # catálogo próprio (ver i18n.md)
├── migrations/
└── tests/               # unit/ e integration/ (ver testing.md)
```

`apps/core/` é a exceção: guarda o que é transversal — mixins de model, value objects
genéricos, templatetags, os comandos de i18n do projeto (`makemessages`,
`compilemessages`), as sondas de saúde.

## As camadas, e o que vai em cada uma

| Camada | Responsabilidade | Pode importar |
| --- | --- | --- |
| `models/` | forma dos dados, constraints, managers | Django, `apps.core.models` |
| `domain/` | regra de negócio pura e valores validados | Pydantic, stdlib — **não** importa model |
| `services/` | efeito colateral: rede, e-mail, storage, terceiros | tudo |
| `presenters.py` | derivar o que a apresentação consome | model, `domain/` |
| `api/`, `views.py` | traduzir request → chamada → resposta | tudo, mas sem regra própria |

A regra que sustenta a tabela: **quanto mais para cima, menos dependência**. Cálculo que
não precisa de banco (`calculate_age`) mora em `domain/services.py` e é testável sem
`django_db`. View e endpoint são casca: se um deles tem `if` de negócio, o `if` está no
lugar errado.

`domain/value_objects/` são modelos Pydantic (`PersonName`, `PhoneNumber`) usados como
tipo de valor em vez de `str` solta — validam na construção e concentram a formatação.
Sobre `@computed_field` em cima de `@property`: é o padrão do Pydantic v2 aqui, e o
`prop-decorator` do MyPy está desligado por isso no `pyproject.toml`.

## Models

- Herde de `apps.core.models.BaseModel` (PK UUID + timestamps) por padrão. Precisa de
  menos, use o mixin direto: `UUIDPrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteModel`,
  `SortableMixin`, `PersonNameMixin`, `PhoneNumberMixin`.
- `SoftDeleteModel` troca `delete()` por marcação em `deleted_at`. O manager `objects` já
  filtra os vivos; `all_objects` vê todos. Quem precisa apagar de verdade chama
  `hard_delete()`.
- Model é pacote (`models/__init__.py` reexportando) assim que passa de um arquivo.
- **Toda mudança de model exige migration no mesmo commit** — o CI roda
  `makemigrations --check --dry-run`. Migrations ficam fora do Ruff e do MyPy.
- Texto exibido ao usuário é traduzível (`gettext_lazy` em `verbose_name`, choices e
  mensagens de validação). Ver [`i18n.md`](i18n.md).

## API (django-ninja)

- Um router por app em `api/router.py`, endpoints em `api/endpoints/<assunto>.py`,
  schemas em `api/schemas.py`. O registro central é `config/urls/api.py`.
- A `NinjaAPI` exige `django_auth` globalmente e usa `ORJSONRenderer` — endpoint não
  precisa (nem deve) repetir isso. Como a autenticação é global, `request.user` nunca é
  anônimo dentro de um endpoint: o `cast("User", request.user)` que aparece em
  `api/endpoints/profile.py` é essa garantia, não um atalho.
- O endpoint devolve schema ou presenter, nunca model cru.

## Configuração

Dois lugares, com critério (ver [ADR 0001](../adr/0001-settings-do-framework-separados-da-configuracao-da-aplicacao.md)):

- **`config/settings/`** — o que o Django e apps de terceiros leem por nome. Partido em
  `parts/`, um módulo por assunto, cada um com `__all__`. **A ordem dos imports em
  `base.py` é semântica**: os parts mutam `INSTALLED_APPS`/`MIDDLEWARE` em sequência, o
  arquivo é `# ruff: noqa: I001` de propósito e `observability` fica por último.
- **`config/app_settings/`** — configuração da aplicação, tipada com `pydantic-settings`:
  `AppSettings` (`APP_`), `FeatureSettings` (`FEATURE_`), `IntegrationSettings`
  (`INTEGRATION_`). Consumida por `get_app_settings()` e irmãos, com `lru_cache`.

Variável nova de aplicação é campo em um desses modelos e linha no `.env.example` — nunca
`getattr(settings, "X", default)` espalhado pelo código. Note que o cache dos acessores é
por processo: mudar `.env` exige reiniciar.

## Tasks

`tasks.py` no app, task decorada com `@shared_task` (não `@app.task`, para o módulo não
importar a instância do Celery) e `name` explícito. O autodiscover encontra pelo nome do
arquivo. Task recebe dado serializável — id, não instância de model.

## Funções e classes

- **Função tem preferência sobre classe.** Classe só quando há ganho real e concreto:
  estado compartilhado entre métodos (`BasePresenter`, que guarda `obj` e empresta
  `__getattr__`), contrato exigido por um framework (`TemplateView`, `RootModel` e
  `BaseModel` do Pydantic) ou necessidade de herança de verdade. Lógica que roda uma vez e
  devolve um valor é função (`calculate_age`, `gravatar_url`), não um `Service` com um
  método.
- **Injeção de dependência é por parâmetro.** Cliente HTTP, horário, configuração ou
  repositório entram como argumento da função, não como import de singleton lido dentro
  do corpo. `calculate_age(birth_date)` recebe a data em vez de chamar
  `timezone.now()` por dentro — é o que permite testar sem mockar import.

## Tipagem e docstrings

- MyPy roda **`strict`** e o job `typecheck` falha em qualquer erro. Não introduza `Any`
  nem `type: ignore` sem comentário ao lado dizendo o motivo — os que já existem seguem
  esse padrão.
- Anote tudo em código de produção, incluindo retorno. Testes podem ficar sem anotação.
- **Docstring no padrão Google, em inglês**: resumo em uma linha, parágrafo de contexto
  quando precisa, `Args:`/`Returns:`/`Raises:`/`Attributes:`. Sem repetir o tipo entre
  parênteses quando já existe type hint — `birth_date: The birth date...`, não
  `birth_date (datetime): ...` (alguns arquivos anteriores a esta convenção, como
  `gravatar.py`, ainda repetem o tipo; não são o modelo a seguir). Toda classe pública tem
  uma; função trivial não precisa.
- Comentário explica **por que**, nunca o quê.
- **Idioma**: todo código de produção — identificadores, docstrings, mensagens de log e
  de exceção — em inglês. Comentários de "por quê" em português sem acento. Alguns
  módulos de infraestrutura herdados da base (o `makemessages` customizado, a task de
  exemplo) têm identificadores em português — é herança, não o padrão para código novo.

## Logs

`structlog` com logger nomeado (`structlog.get_logger("app.events")`) e evento como
primeiro argumento, contexto como kwargs: `logger.info("core.echo", mensagem=...)`. O
correlation id entra sozinho, via `django-guid`, e sai no header `X-Correlation-Id` — não
o propague à mão.
