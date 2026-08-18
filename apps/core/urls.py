from django.urls import path
from health_check.views import HealthCheckView

from apps.core.views import HomeView, ping

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("ping/", ping, name="ping"),
    path(
        "health/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
                "health_check.Database",
            ],
        ),
        name="health_check",
    ),
]
