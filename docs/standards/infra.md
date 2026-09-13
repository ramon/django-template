# Padrões: infraestrutura local e de deploy

Onde os processos rodam, o que cada imagem contém e as paridades que precisam ser mantidas
à mão. A narrativa — como a imagem multi-stage é construída, storage remoto, observabilidade
— fica no [`README.md`](../../README.md#imagens-docker); aqui ficam as regras e os comandos.

## Os dois caminhos de desenvolvimento

Chegam ao mesmo lugar; muda onde o processo roda. **Não misture os dois na mesma sessão**:
o `.venv` da máquina e o `/opt/venv` do container não são o mesmo ambiente, e a confusão
aparece como dependência "instalada" que o processo não vê.

### Stack inteira em containers

```bash
cp .env.example .env                       # SECRET_KEY não tem default
docker compose up                          # app (migrado), worker, beat, Vite, banco, cache
docker compose --profile observability up  # + Prometheus em :9090
```

O código é bind mount, então o autoreload continua valendo — **só mudança de dependência
exige rebuild** (`docker compose build app`). O `frontend` tem volume próprio para
`node_modules`: os binários nativos instalados lá são musl, e sobrescrever com os da máquina
quebra o Vite.

Dentro dos containers os binários já estão no PATH (`/opt/venv/bin`); **`uv run` aqui é
errado**:

```bash
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
docker compose exec app pytest
docker compose exec app mypy apps tests
docker compose exec app ruff check . --fix
docker compose exec frontend bun run lint
docker compose exec frontend bun run test
docker compose logs -f worker              # ver a task cair na fila
```

### Só banco e cache em containers

```bash
uv sync && bun install
make services                              # database + kv-database, com 5432/6379 no host
python manage.py migrate
python manage.py runserver                 # usa config.settings.development
bun run dev                                # Vite com HMR na porta VITE_PORT (8001)
```

`make services` sobe os dois com `-f docker-compose.yml -f docker-compose.local-db.yml` —
é esse segundo arquivo que publica `5432`/`6379` no host, e ele **não** entra no `docker
compose up` da stack inteira. `docker compose up -d database` cru não expõe porta nenhuma.

O resto dos comandos com `uv run` — ver [`testing.md`](testing.md) e
[`git.md`](git.md#o-que-o-ci-verifica).

### O que não roda no container de dev

O `Dockerfile.dev` é um estágio só, com as dependências de dev e nada além:

- **i18n** — não instala `gettext`, então `makemessages` e `compilemessages` falham lá
  dentro. Rode na máquina. (A imagem de produção instala, no estágio `assets`, porque
  compilar é passo de build.)
- **e2e** — exigem os browsers do Playwright (Chromium e WebKit), que a imagem não traz.

Acrescentar qualquer um dos dois à imagem de dev é uma decisão, não um detalhe: pesa no
build de todo mundo. Se for fazer, registre o ADR.

## Serviços e portas

| Serviço | Porta interna | Publica no host | Imagem | Papel |
| --- | --- | --- | --- | --- |
| `app` | 8000 | `127.0.0.1:${APP_PORT:-8000}` | `Dockerfile.dev` | migra e sobe o `runserver` |
| `frontend` | `${VITE_PORT:-8001}` | `127.0.0.1:${VITE_PORT:-8001}` | `oven/bun` | dev server do Vite, com HMR |
| `worker` | — | — | `Dockerfile.dev` | worker do Celery |
| `beat` | — | — | `Dockerfile.dev` | scheduler do Celery |
| `database` | 5432 | só via `make services` (`${POSTGRES_PORT:-5432}`) | `postgres:18-alpine` | com healthcheck; `app` espera por ele |
| `kv-database` | 6379 | só via `make services` (`${VALKEY_PORT:-6379}`) | `valkey:9-alpine` | cache, sessão e broker (DBs 0, 1 e 2) |
| `prometheus` | 9090 | `127.0.0.1:${PROMETHEUS_PORT:-9090}` | `prom/prometheus` | atrás do profile `observability` |

Só `app`, `frontend` e `prometheus` publicam porta no `docker-compose.yml`, presos a
`127.0.0.1` e com a porta vinda do `.env` (default = valor de sempre). `database` e
`kv-database` não publicam nada — de dentro do compose os serviços se acham pelo nome, e
do host o acesso é `docker compose exec database psql -U user app` /
`docker compose exec kv-database valkey-cli`. Para expor `5432`/`6379` no host (caminho da
app na máquina), `make services` carrega o `docker-compose.local-db.yml` — ver
[ADR 0016](../adr/0016-portas-do-compose-internas-por-padrao.md).

**Colisão de porta** (outra stack Docker no ar): mude o número no `.env` — `APP_PORT`,
`VITE_PORT`, `PROMETHEUS_PORT`, `POSTGRES_PORT`, `VALKEY_PORT` — e, para `POSTGRES_PORT`/
`VALKEY_PORT`, reflita a mesma porta em `DATABASE_URL`/`CACHE_URL`/`SESSION_CACHE_URL`/
`CELERY_BROKER_URL`. `COMPOSE_PROJECT_NAME` no `.env` separa os nomes de container/rede/
volume entre clones.

O bloco `x-app` concentra build, `env_file` e volumes dos três serviços de Python, e
sobrescreve `DATABASE_URL`, `CACHE_URL`, `SESSION_CACHE_URL` e `CELERY_BROKER_URL` — dentro
da rede do compose os serviços se acham pelo nome, não por `127.0.0.1`. **Serviço novo de
Python usa o `x-app`**, em vez de repetir a configuração.

## Processos: `Procfile` e compose andam juntos

São quatro tipos, declarados no `Procfile`: `release` (o `migrate`), `web` (gunicorn com
worker uvicorn), `worker` e `beat` (Celery). A imagem de produção carrega o arquivo, então
plataformas que o leem (Heroku, Railway, Render, Dokku) reconhecem os quatro, e o job
`docker` do CI espelha a sequência — `release` migra, `web` serve.

Os serviços `app`, `worker` e `beat` do `docker-compose.yml` são esses mesmos processos em
desenvolvimento, com o comando de Celery idêntico ao do `Procfile`.

**Processo novo entra nos dois lugares**, com o mesmo comando: tipo no `Procfile`, serviço no
`docker-compose.yml`. Só no `Procfile` é uma fila que ninguém consome em desenvolvimento; só
no compose é uma fila que não existe em produção — e as duas falhas aparecem tarde. Mesma
regra ao mudar o comando de um processo: os dois arquivos, no mesmo commit.

## Variáveis de ambiente

`.env.example` é o espelho de tudo que o projeto lê, com os valores que casam com o
compose. **Variável nova entra lá no mesmo commit**, com o comentário do que ela faz — é o
único inventário que existe, e um `.env.example` incompleto quebra o próximo setup, não o
seu.

O prefixo diz de onde ela é lida: sem prefixo, é settings do framework (`django-environ`,
em `config/settings/parts/`); com `APP_`, `FEATURE_` ou `INTEGRATION_`, é configuração da
aplicação (`pydantic-settings`, em `config/app_settings/`) — ver
[`backend.md`](backend.md#configuração). `SECRET_KEY` é a única sem default: o boot falha
sem ela, de propósito.

`APP_PORT`, `VITE_PORT`, `PROMETHEUS_PORT`, `POSTGRES_PORT`, `VALKEY_PORT` e
`COMPOSE_PROJECT_NAME` são lidas pelo `docker compose` (o `pydantic-settings` ignora
extras, então `APP_PORT` não conflita com o prefixo `APP_`). Servem para conviver com
outra stack Docker — ver [ADR 0016](../adr/0016-portas-do-compose-internas-por-padrao.md).

Duas delas também são lidas fora do compose, para que a porta exista num lugar só:

- `VITE_PORT` — o `vite.config.mjs` escuta nela (`server.port`, e o container do
  `frontend` publica a mesma porta dos dois lados), e `config/settings/parts/vite.py`
  monta com ela `VITE_DEV_SERVER_URL`, a URL que `{% vite_js %}` entrega ao browser.
  `VITE_DEV_SERVER_URL` pode ser definida direto quando o dev server não está em
  `127.0.0.1`.
- `APP_PORT` — o `vite.config.mjs` libera CORS para `localhost` e `127.0.0.1` nessa
  porta. No caminho sem Docker, `runserver` sobe em 8000 independente dela: quem roda o
  Django em outra porta ajusta `APP_PORT` no `.env` para o CORS acompanhar.

## Imagens

| Arquivo | Estágios | Uso |
| --- | --- | --- |
| `Dockerfile.dev` | um | compose (`app`, `worker`, `beat`), com código em volume |
| `Dockerfile` | `frontend` → `deps` → `assets` → `runtime` | produção |

A separação de produção existe para o runtime não herdar ferramenta de build: o bundle do
Vite sai do estágio com Bun, o `.venv` de um com uv (`--no-dev`), o `collectstatic` e os
`.mo` de um que tem os dois. O `runtime` parte de `python:3.14-slim-bookworm` e recebe só o
`.venv`, o código, `public/` e o manifest.

**Regra, verificada pelo job `docker` do CI**: a imagem final não pode conter `uv`, `bun`,
`node`, `npm`, `gcc` nem dependência de dev (`pytest`, `mypy`, `ruff`, `debug_toolbar`,
`factory`, `faker`, `playwright`, `coverage`). Quem acrescenta um `RUN` no estágio final é
responsável por não vazar nenhum dos dois.

Dois build args, ambos com default seguro: `COMPILE_BYTECODE=0` troca ~60 MB por latência
no primeiro request de cada worker, e `UV_EXTRA=s3` inclui o extra de storage remoto.

## Verificando a imagem de produção

`docker compose up` usa o `Dockerfile.dev` e **não** exercita a imagem de produção. Para
testá-la como o CI faz:

```bash
docker build -t app:prod .
docker run --rm --env-file .env app:prod python manage.py migrate --noinput
docker run --rm -p 8000:8000 --env-file .env app:prod
curl -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/health/
```

O header não é decoração: em produção `SECURE_SSL_REDIRECT` está ligado e sem ele toda
requisição volta 301 — é também por isso que o `HEALTHCHECK` da imagem o envia. O processo
roda como usuário sem privilégio; comando que precise escrever tem que escrever em lugar
que ele possa.

## Sondas de saúde

| Rota | Verifica | Para quem |
| --- | --- | --- |
| `/health/` | banco, os dois aliases de cache e o storage | balanceador / readiness |
| `/health/workers/` | worker do Celery respondendo ao ping | monitoração |

A lista vive em `READINESS_CHECKS`, em `apps/core/urls.py`. **Check novo em `/health/` só se
for dependência da request**: o worker está fora de propósito — derrubar a aplicação do
balanceador porque uma fila caiu troca falha parcial por total — e DNS e e-mail também, por
fazerem chamada externa e deixarem a sonda instável.

O check de storage grava, lê e apaga um arquivo por requisição; com storage remoto, isso é
uma ida à rede por probe. É o preço de saber que o bucket responde.
