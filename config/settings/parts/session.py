from config.settings.parts.django import DEBUG

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_SECURE = not DEBUG  # Only send cookie over HTTPS
SESSION_COOKIE_HTTPONLY = True  # JavaScript can't access the cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Prevents cross-site request attacks
SESSION_COOKIE_AGE = 1209600  # Two weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_CACHE_ALIAS = "session"