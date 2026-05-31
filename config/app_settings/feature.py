from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureSettings(BaseSettings):
    """
    Handles feature-specific settings and configurations.

    This class is designed to manage and load settings related to application
    features. It utilizes a configuration management system that supports
    environment variable-based configuration. The settings can be loaded from
    a specified `.env` file and customized with a defined prefix and other
    configuration options.

    Attributes:
        model_config (SettingsConfigDict): Configuration dictionary to define
            environment-related settings, including file path, encoding,
            variable prefix, and additional options for feature-specific settings.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="FEATURE_",
        env_nested_delimiter="__",
        extra="ignore"
    )


@lru_cache(maxsize=1)
def get_feature_settings() -> FeatureSettings:
    return FeatureSettings()