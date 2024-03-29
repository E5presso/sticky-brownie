import os
from enum import StrEnum
from typing import ClassVar, TypeAlias
from pathlib import Path
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict
from spakky.cryptography.key import Key
from spakky.stereotype.configuration import Configuration

DotenvType: TypeAlias = Path | str | list[Path | str] | tuple[Path | str, ...]


class Environment(StrEnum):
    DEV = "development"
    PROD = "production"


PYTHON_ENV: Environment = Environment(os.getenv("PYTHON_ENV", Environment.DEV.value))


class DatabaseSetting(BaseSettings):
    url: str = ""
    pool_size: int = 1


class TokenSetting(BaseSettings):
    secret: str = ""
    is_urlsafe: bool = False
    expire_after_in_hours: int = 0

    @property
    def secret_key(self) -> Key:
        return Key(base64=self.secret, url_safe=self.is_urlsafe)

    @property
    def expire_after(self) -> timedelta:
        return timedelta(hours=self.expire_after_in_hours)


@Configuration()
class Config(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )
    debug: bool = False
    database: DatabaseSetting = DatabaseSetting()
    token: TokenSetting = TokenSetting()

    def __init__(self) -> None:
        if PYTHON_ENV == Environment.DEV:
            super().__init__(_env_file=".env.development")
        if PYTHON_ENV == Environment.PROD:
            super().__init__()
