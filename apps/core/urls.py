from django.urls import path
from health_check.views import HealthCheckView

from apps.core.views import HomeView, ping

app_name = "core"

# O que a request precisa para ser atendida: banco, os dois aliases de cache e o
# storage. Fora daqui de proposito:
#   - DNS e Mail, que fazem chamada externa e tornam a sonda instavel;
#   - o worker do Celery, que nao e' dependencia do processo web -- derrubar a app
#     do balanceador porque uma fila caiu troca uma falha parcial por uma total.
READINESS_CHECKS = [
    "health_check.Database",
    "health_check.Cache",
    # SESSION_CACHE_ALIAS aponta para "session": se este cair, ninguem loga.
    ("health_check.Cache", {"alias": "session"}),
    # grava, le e apaga um arquivo a cada sonda; com storage remoto isso e' uma
    # ida a' rede por probe, e e' o unico jeito de saber que o bucket responde.
    "health_check.Storage",
]

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("ping/", ping, name="ping"),
    path(
        "health/",
        HealthCheckView.as_view(checks=READINESS_CHECKS),
        name="health_check",
    ),
    path(
        # separado da sonda do balanceador de proposito (ver READINESS_CHECKS)
        "health/workers/",
        HealthCheckView.as_view(checks=["health_check.contrib.celery.Ping"]),
        name="health_check_workers",
    ),
]
