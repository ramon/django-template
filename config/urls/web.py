from django.urls import include, path

urlpatterns = [
    path('auth/', include('allauth.urls')),
    path("", include("apps.accounts.urls")),
]
