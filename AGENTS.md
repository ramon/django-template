# AGENTS.md

Instruções canônicas para agentes neste repositório. Vale para Claude Code, OpenCode,
Codex, Cursor, Gemini CLI e qualquer harness que leia `AGENTS.md`. Os arquivos
específicos de harness (`CLAUDE.md`) apenas apontam para cá — regra nova entra aqui,
não lá.

Este arquivo veio do `django-template` e **vale tanto para o template quanto para
qualquer projeto gerado a partir dele**: o que está descrito aqui são as convenções da
base, que o projeto herda no dia zero e continua carregando enquanto não decidir o
contrário — e, quando decidir, o lugar de registrar é um ADR
([`docs/adr/`](docs/adr/README.md)), com a atualização desta página no mesmo commit.
Nada aqui pressupõe que o repositório ainda seja o template.

## A arquitetura em um parágrafo

Projeto Django server-rendered: Django 6 renderiza o HTML e serve a API (django-ninja),
o Vite é só pipeline de assets, e o cliente é enriquecido progressivamente com HTMX,
Stimulus e Alpine. Não há SPA nem pasta `backend/` — `manage.py`, `apps/` e `config/`
vivem na raiz, e cada app em `apps/` é um contexto de domínio. Stack, instalação e
execução ficam no [`README.md`](README.md), que é a referência para *como rodar* este
projeto; este arquivo trata de *como trabalhar* nele.

## A pasta `docs/`

`docs/` é a memória de decisão do projeto e a sua primeira parada antes de escrever
código:

| Pasta | O que guarda | Leia quando |
| --- | --- | --- |
| [`docs/standards/`](docs/standards/) | como se escreve código aqui: camadas, nomes, tipagem, testes, i18n, infra, git | sempre, antes de editar a área correspondente |
| [`docs/adr/`](docs/adr/) | decisões arquiteturais, com o motivo e as alternativas descartadas | antes de mudar ou contrariar uma decisão estrutural |
| [`docs/specs/`](docs/specs/) | especificações de features: comportamento esperado, regras, casos de borda | antes de implementar uma feature especificada |
| [`docs/plans/`](docs/plans/) | planos de implementação de trabalhos multi-etapa | ao retomar ou continuar um trabalho em andamento |

Como usar:

- **Antes de codar**: leia o padrão da área que vai tocar. Se a tarefa tem spec ou
  plano em `docs/`, ele manda — divergência entre spec e código é bug, não licença.
- **Ao decidir algo estrutural** (trocar biblioteca, mudar camada, criar convenção):
  registre um ADR em `docs/adr/`, seguindo [`0000-template.md`](docs/adr/0000-template.md).
  Numere sequencialmente — continuando de onde os ADRs herdados param — e adicione a
  linha no índice do [`docs/adr/README.md`](docs/adr/README.md).
- **Os ADRs 0001–0006 vêm da base e valem por padrão.** Para contrariar um deles, escreva
  um ADR novo que o substitua; não edite o antigo nem simplesmente faça diferente no
  código.
- **Em trabalho longo** (várias etapas, várias sessões): mantenha o plano em
  `docs/plans/` atualizado conforme avança, para que a próxima sessão retome do estado
  real e não do zero.
- **Ao mudar comportamento documentado**: atualize o documento no mesmo commit. Doc
  desatualizada em `docs/` é pior que doc ausente, porque agentes a tratam como verdade.
- **Não duplique**: setup, comandos e stack ficam no `README.md`; `docs/standards/`
  linka para ele em vez de repetir.

## Começando um projeto a partir desta base

Num repositório recém-gerado há código que existe só para provar que a stack subiu. Ele é
scaffolding, não patrimônio — a primeira feature real substitui:

- **Página de exemplo**: `HomeView`, `ping` e `build_diagnostics` em `apps/core/views.py`,
  as rotas `home`/`ping` em `apps/core/urls.py`, `templates/pages/home.html` e
  `templates/pages/partials/ping.html`. Ao apagá-los, vão junto
  `apps/core/tests/integration/test_home_view.py` e `tests/e2e/test_home.py`.
- **Task de exemplo**: `echo` em `apps/core/tasks.py`, com
  `apps/core/tests/unit/test_tasks.py`.
- **Controller de exemplo**: `frontend/controllers/hello_controller.js` e seu teste.
- **Identidade do projeto**: `name`, `description` e `authors` no `pyproject.toml`, o
  `README.md` e o `LICENSE`.

Fica tudo o mais: `apps/core/` (mixins, value objects, templatetags, sondas de saúde, o
`makemessages` customizado), `apps/accounts/` (User e Profile), `config/` inteiro,
`frontend/lib/`, `templates/layouts/`, `conftest.py` e as sondas `/health/`. Apagar uma
sonda ou um mixin porque "não está sendo usado ainda" é remover base, não exemplo.

## Comandos

Dois caminhos, e eles não se misturam na mesma sessão: o `.venv` da máquina e o `/opt/venv`
do container não são o mesmo ambiente. Serviços, portas, imagens, processos e sondas estão
em [`docs/standards/infra.md`](docs/standards/infra.md).

### Com a stack em containers

```bash
cp .env.example .env                      # SECRET_KEY não tem default
docker compose up                         # app (migrado), worker, beat, Vite, banco, cache
docker compose exec app pytest            # binários no PATH da imagem: sem `uv run` aqui
docker compose exec frontend bun run test
```

**i18n e e2e não rodam no container de dev** — falta `gettext` e falta o Chromium do
Playwright. Esses dois são trabalho de máquina.

### Na máquina, com banco e cache em container

```bash
uv sync && bun install
docker compose up -d database kv-database
python manage.py migrate
python manage.py runserver                # usa config.settings.development
bun run dev                               # Vite com HMR na porta 8001

uv run ruff check . --fix && uv run ruff format .
uv run mypy apps tests                    # strict
uv run pytest                             # usa config.settings.test
uv run pytest -m e2e                      # fora do default; exige `bun run build`
bun run lint && bun run test

python manage.py makemessages             # idiomas de settings.LANGUAGES; sem flags,
                                          # o comando do projeto já as aplica
python manage.py compilemessages          # idem: ignora .venv e node_modules por padrão
python manage.py makemigrations
```

Os dois `manage.py makemessages`/`compilemessages` acima já são os comandos customizados do
projeto (`apps/core/management/commands/`) — nenhum dos dois precisa de `--ignore` na linha
de comando; sem eles, o `compilemessages` nativo recompilaria os ~1300 catálogos do `.venv`
e o que viesse de `node_modules` ([`i18n.md`](docs/standards/i18n.md)).

## Regras que quebram o CI se ignoradas

1. **A ordem dos imports em `config/settings/base.py` é semântica.** Os parts mutam
   `INSTALLED_APPS`/`MIDDLEWARE` em sequência; o arquivo é `# ruff: noqa: I001` de
   propósito. Não reordene, e mantenha `observability` por último.
2. **Settings do framework em `config/settings/` (django-environ), configuração de
   aplicação em `config/app_settings/` (pydantic-settings).** Feature nova não vira
   variável solta em settings: vira campo em `AppSettings`, `FeatureSettings` ou
   `IntegrationSettings`, com o prefixo correspondente.
3. **String traduzível nova exige `makemessages` no mesmo commit.** O comando é
   idempotente aqui, então o CI compara o diff dos `.po` e falha se houver qualquer um.
   Os `.po` são versionados; os `.mo`, não.
4. **Mudança em model exige migration no commit.** O CI roda
   `makemigrations --check --dry-run`.
5. **MyPy roda `strict`, e o job `typecheck` falha em qualquer erro.** Não introduza
   `Any` nem `type: ignore` sem comentário ao lado dizendo o porquê — é o padrão dos
   silenciamentos que já existem no `pyproject.toml`.
6. **Classe CSS segue BEM** (`bloco__elemento--modificador`, kebab-case), validado pelo
   Stylelint e coberto por `frontend/styles/bem.test.js`. Mudar a regra sem atualizar o
   teste quebra o CI.
7. **A chave do `{% vite_css %}`/`{% vite_js %}` é o caminho do input relativo à raiz**
   (`frontend/entries/app.js`), não o nome do bundle. Entrypoint novo entra em
   `vite.config.mjs`.
8. **Nunca comite `.env`, `.mo`, `static/dist/` nem nada em `public/static/`.**
9. **A imagem de produção não pode conter `uv`, `bun`, `node`, compilador ou dependência
   de dev** — o job `docker` do CI verifica. Mesma regra para a paridade
   `Procfile` ↔ `docker-compose.yml`: processo novo entra nos dois
   ([`infra.md`](docs/standards/infra.md)).

## Estilo

- **Idioma**: todo código de produção — identificadores, docstrings, logs e mensagens de
  exceção — em inglês. Comentários que explicam *por que* em português, sem acento (é o
  padrão do código existente:
  `# a NinjaAPI exige django_auth globalmente, entao o usuario nunca e' anonimo aqui`).
  Prosa em Markdown — README e `docs/` — em português com acento.
- **Comentário só para o "por quê".** O "o quê" está no código. Comentário que repete a
  linha seguinte é ruído; comentário que explica uma escolha não óbvia é o que impede
  alguém de desfazê-la sem saber.
- **Docstrings no padrão Google, em inglês**: resumo em uma linha, contexto quando
  precisa, `Args:`/`Returns:`/`Raises:`/`Attributes:`, sem repetir o tipo entre parênteses
  quando já existe type hint. Nem toda função precisa de uma; toda classe pública precisa.
- **Função tem preferência sobre classe.** Classe só entra com ganho claro: estado
  compartilhado entre métodos, contrato de framework (`TemplateView`, model do Pydantic)
  ou herança de verdade. Ver [`backend.md`](docs/standards/backend.md).
- **Injeção de dependência por parâmetro.** Cliente, horário, configuração ou repositório
  entram como argumento, não como singleton lido de dentro da função.
- **Tipagem completa** em código de produção, MyPy `strict`. Testes podem ficar sem
  anotação (`disallow_untyped_defs = false` para `tests.*`).
- **Commits**: Conventional Commits em português, sem acento, no imperativo —
  `feat(accounts): dar catalogo proprio a cada app`. O escopo é o app ou a área.
- Formatação é assunto do Ruff e do Biome; não ajuste espaçamento à mão.

## Antes de dizer que terminou

Qual gate se aplica a qual mudança, a ordem de execução e por que cada um existe estão em
[`docs/standards/quality-gates.md`](docs/standards/quality-gates.md). A lista abaixo é o
que rodar; aquele documento explica o quando e o porquê.

Na máquina, com `uv run`; via Docker, com `docker compose exec app` e sem o `uv run`.

- [ ] `uv run ruff check . && uv run ruff format --check .`
- [ ] `uv run mypy apps tests`
- [ ] `uv run pytest` (e `-m e2e` se a mudança chega ao browser)
- [ ] `bun run lint && bun run test:coverage`, se mexeu em JS ou CSS
- [ ] `makemessages` / `makemigrations`, se o caso pede
- [ ] `docs/` atualizada: ADR para decisão nova, padrão revisado se a convenção mudou
- [ ] relate o que rodou e o que viu, não o que deveria funcionar
