from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IntegrationSettings(BaseSettings):
    """
    Handles integration settings for the application.

    This class is responsible for loading and managing integration-related
    configuration settings. It provides functionality to read settings from
    an environment file, supports nested configuration via specified delimiters,
    and adheres to the defined environment variable prefixes. Any extra or
    unrecognized configuration keys are ignored to ensure strict compliance
    with defined settings.

    Attributes:
        model_config (SettingsConfigDict): Configuration for the settings class,
            including environment file details, nested delimiter, prefix for
            environment variables, and policy for handling extra keys.
        SENTRY_DSN (SecretStr | None): Optional Sentry Data Source Name (DSN)
            used for integration with Sentry error tracking. Defaults to None
            if not provided.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INTEGRATION_",
        env_nested_delimiter="__",
        extra="ignore"
    )

    SENTRY_DSN: SecretStr | None = None


@lru_cache(maxsize=1)
def get_integration_settings() -> IntegrationSettings:
    return IntegrationSettings()
