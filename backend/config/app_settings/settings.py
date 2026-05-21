from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, StrEnum):
    """
    Represents different environment types for deployment and configuration.

    This class enumerates the possible environment types where an application
    can be deployed. It is intended for use in configurations, logging, or
    environment-specific behavioral control. Each enum value corresponds
    to a specific deployment tier.

    Attributes:
        LOCAL (str): Represents a local development environment.
        TEST (str): Represents a testing environment used for quality
            assurance and other non-production validation.
        STAGING (str): Represents a staging environment that mirrors
            production for final testing before deployment.
        PRODUCTION (str): Represents a live production environment
            where the application is accessible to end users.
    """
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    """
    Handles application configuration settings.

    This class is responsible for loading and managing application settings by
    leveraging environment variables. It uses a nested configuration structure
    to map environment variable prefixes and delimiters to application settings.
    The settings support multiple environments and provide flexibility in
    fine-tuning application behavior. The settings are automatically validated
    and loaded during initialization.

    Attributes:
        environment (Environment): The current application execution environment. Possible
            values are defined in the `Environment` enumeration.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="ignore"
    )

    environment: Environment = Environment.LOCAL
    feature: FeatureConfig = FeatureConfig()

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
