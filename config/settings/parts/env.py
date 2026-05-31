import environ
from .paths import ENV_FILE

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(ENV_FILE)

__all__ = ["env"]