"""Views transversais: a pagina inicial de exemplo e o fragmento que ela usa."""

import sys
from typing import Any

import django
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from config.app_settings import get_app_settings


def _short_path(dotted: str) -> str:
    """Ultimo segmento de um caminho pontilhado: 'a.b.RedisCache' -> 'RedisCache'."""
    return dotted.rsplit(".", 1)[-1]


def _frontend_status() -> str:
    """Como os assets estao sendo servidos agora."""
    if settings.DEBUG:
        return "dev server do Vite (bun run dev)"

    manifest = settings.BASE_DIR / "static" / "dist" / ".vite" / "manifest.json"
    return "build do Vite" if manifest.exists() else "build ausente (rode bun run build)"


def build_diagnostics() -> list[tuple[str, str]]:
    """
    Pares rotulo/valor descrevendo a configuracao que esta de fato em uso.

    Le os settings ja resolvidos em vez do ambiente, entao mostra o resultado do
    encadeamento parts/ -> modulo de ambiente, que e' onde moram as surpresas.
    """
    database = settings.DATABASES["default"]

    return [
        ("Django", django.get_version()),
        ("Python", sys.version.split()[0]),
        ("Settings", settings.SETTINGS_MODULE),
        ("APP_ENVIRONMENT", get_app_settings().environment.value),
        ("Banco", f"{_short_path(database['ENGINE'])} ({database['NAME']})"),
        ("Cache", _short_path(settings.CACHES["default"]["BACKEND"])),
        ("Idioma / fuso", f"{settings.LANGUAGE_CODE} / {settings.TIME_ZONE}"),
        ("Frontend", _frontend_status()),
        ("Prometheus", "ligado" if settings.ENABLE_PROMETHEUS else "desligado"),
    ]


class HomeView(TemplateView):
    """
    Pagina de boas-vindas do template.

    Existe para dar um retorno visivel logo apos o `runserver` e para exercitar a
    stack de ponta a ponta: layout cotton, assets do Vite, HTMX, Stimulus e Alpine.
    Substitua por conteudo real assim que o projeto tiver o seu.
    """

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Seu app está no ar"
        # O diagnostico descreve a infraestrutura: so aparece em DEBUG para nao
        # virar reconhecimento gratuito num deploy que ainda usa esta pagina.
        context["diagnostics"] = build_diagnostics() if settings.DEBUG else None
        return context


def ping(request: HttpRequest) -> HttpResponse:
    """Fragmento HTML trocado pelo HTMX, para provar o ciclo request/swap."""
    return render(
        request,
        "pages/partials/ping.html",
        {"server_time": timezone.localtime()},
    )
