# syntax=docker/dockerfile:1
#
# Imagem de producao, em estagios. Nenhuma ferramenta de build sobrevive ate o
# estagio final: nem uv, nem bun, nem node_modules, nem dependencias de dev.
#
#   docker build -t app:prod .
#   docker run --rm -p 8000:8000 --env-file .env app:prod

# ==============================================================================
# 1. frontend -- bundle e manifest do Vite
# ==============================================================================
FROM oven/bun:1-alpine AS frontend

WORKDIR /build

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# O Tailwind 4 varre o projeto atras das classes efetivamente usadas, entao os
# templates precisam estar aqui: sem eles o CSS sai sem metade das regras.
COPY vite.config.mjs ./
COPY frontend/ ./frontend/
COPY templates/ ./templates/
COPY apps/ ./apps/

RUN bun run build

# ==============================================================================
# 2. deps -- .venv apenas com as dependencias de producao
# ==============================================================================
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS deps

# Pre-compilar em .pyc custa ~60 MB na imagem e devolve o primeiro request de
# cada worker sem a pausa da compilacao. Passe --build-arg COMPILE_BYTECODE=0
# para trocar tamanho por latencia inicial.
ARG COMPILE_BYTECODE=1

# Extra opcional do projeto, para nao pagar 31 MB de boto3 sem usar S3:
#   docker build --build-arg UV_EXTRA=s3 .
ARG UV_EXTRA=

ENV UV_COMPILE_BYTECODE=${COMPILE_BYTECODE} \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Camada propria para as dependencias: so refaz o sync quando o lock muda.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev ${UV_EXTRA:+--extra "$UV_EXTRA"}

# ==============================================================================
# 3. assets -- collectstatic com os assets do Vite ja construidos
# ==============================================================================
FROM deps AS assets

COPY . .
COPY --from=frontend /build/static/dist ./static/dist

# SECRET_KEY nao tem default e o collectstatic importa os settings; este valor
# existe so durante o build e nao entra na imagem final.
RUN SECRET_KEY=build-only DJANGO_SETTINGS_MODULE=config.settings.production \
    .venv/bin/python manage.py collectstatic --noinput --clear

# Os .po sao versionados, os .mo nao (.gitignore): a compilacao e' passo de build.
# O comando e' o customizado em apps/core/management/commands/compilemessages.py,
# que ja ignora .venv e node_modules -- o nativo varre a arvore inteira a partir
# do diretorio atual e nao tem ignore nenhum por padrao.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/* \
    && SECRET_KEY=build-only DJANGO_SETTINGS_MODULE=config.settings.production \
       .venv/bin/python manage.py compilemessages

# ==============================================================================
# 4. runtime -- so o que a aplicacao precisa para responder
# ==============================================================================
FROM python:3.14-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}" \
    DJANGO_SETTINGS_MODULE=config.settings.production

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-log-init --create-home app

WORKDIR /app

COPY --from=deps   --chown=app:app /app/.venv   ./.venv
COPY --from=assets --chown=app:app /app/public ./public

# Copia dirigida em vez de `COPY . .`: mantem configs de lint e toolchain de fora
# da imagem final. Vem do estagio assets, e nao do contexto, para trazer junto os
# catalogos ja compilados (os .mo ficam ao lado dos .po, dentro de cada app).
COPY --from=assets --chown=app:app /app/manage.py /app/Procfile ./
COPY --from=assets --chown=app:app /app/config    ./config/
COPY --from=assets --chown=app:app /app/apps      ./apps/
COPY --from=assets --chown=app:app /app/templates ./templates/
COPY --from=assets --chown=app:app /app/locale    ./locale/

# O unico pedaco do build do Vite que e' lido em runtime: {% vite_js %} resolve a
# entrada por aqui. Os bundles em si ja foram publicados em public/static/ pelo
# collectstatic, com hash no nome.
COPY --from=frontend --chown=app:app /build/static/dist/.vite ./static/dist/.vite

USER app

EXPOSE 8000

# A producao roda atras de um proxy que termina TLS (SECURE_PROXY_SSL_HEADER);
# sem o X-Forwarded-Proto o SECURE_SSL_REDIRECT devolveria 301 para a sonda.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import sys,urllib.request as u; r=u.Request('http://127.0.0.1:8000/health/', headers={'X-Forwarded-Proto':'https'}); sys.exit(0 if u.urlopen(r, timeout=4).status == 200 else 1)"]

# WEB_CONCURRENCY define o numero de workers; o gunicorn le a variavel sozinho.
CMD ["gunicorn", "config.asgi:application", \
     "--worker-class", "uvicorn_worker.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-"]
