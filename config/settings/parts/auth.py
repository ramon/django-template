# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
from config.settings.parts.django import INSTALLED_APPS, MIDDLEWARE

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.usersessions',
    'allauth.mfa'
]

MIDDLEWARE += [
    'allauth.account.middleware.AccountMiddleware',
    'allauth.usersessions.middleware.UserSessionsMiddleware'
]

LOGIN_REDIRECT_URL = '/'

# Allauth settings
## User Model
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

### Signup
ACCOUNT_SIGNUP_FIELDS = ['name*', 'email*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {"email"}

### Login
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_TRUST_ENABLED = True

### Logout
ACCOUNT_LOGOUT_ON_GET = True

### Email Verification
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True

## MFA
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_TRUST_ENABLED = True

SOCIALACCOUNT_PROVIDERS = {}

USERSESSIONS_TRACK_ACTIVITY = True