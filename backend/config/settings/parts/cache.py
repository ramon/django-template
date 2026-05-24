from parts.env import env

# Cache
# https://docs.djangoproject.com/en/6.0/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.cache_url("CACHE_URL", default="redis://127.0.0.1:6379/0"),
    },
}