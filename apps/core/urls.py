from django.urls import path
from health_check.views import HealthCheckView

app_name = "core"

urlpatterns = [
    path("health/", HealthCheckView.as_view(
        checks=[
            "health_check.Cache",
            "health_check.Database",
        ],
    ), name="health_check"),
]