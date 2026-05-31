from .django import INSTALLED_APPS

INSTALLED_APPS += [
    "apps.core",
    "apps.accounts",
]

AUTH_USER_MODEL = "accounts.User"