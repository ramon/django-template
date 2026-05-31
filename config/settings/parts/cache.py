from .env import env

# Cache
# https://docs.djangoproject.com/en/6.0/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str("CACHE_URL", default="redis://127.0.0.1:6379/0"),
        "KEY_PREFIX": env.str("CACHE_PREFIX", "cache"),
    },
    "session": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str("SESSION_CACHE_URL", default="redis://127.0.0.1:6379/1"),
        "KEY_PREFIX": env.str("SESSION_CACHE_PREFIX", "session"),
    },
}