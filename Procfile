# Declaracao de processos para plataformas que leem Procfile (Heroku, Railway,
# Render, Dokku). A imagem de producao carrega este arquivo, entao a mesma
# definicao serve para `docker run` e para a plataforma.
release: python manage.py migrate --noinput
web: gunicorn config.asgi:application --worker-class uvicorn_worker.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --access-logfile -
worker: celery --app config worker --loglevel INFO
beat: celery --app config beat --loglevel INFO
