"""Чтение и строгая проверка TOML-конфигурации."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .errors import AppError

MAX_DEPTH = 100
FIELDS = {"package", "repository", "test_mode", "version",
          "max_depth", "filter_substring"}
PACKAGE = r"(?:@[a-z0-9._-]+/)?[a-z0-9][a-z0-9._-]*"
VERSION = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"


@dataclass(frozen=True)
class Config:
    """Шесть параметров пользователя и разрешённый путь репозитория."""

    package: str
    repository: str
    test_mode: bool
    version: str
    max_depth: int
    filter_substring: str


def validate_fields(data):
    """Проверить полноту и типы параметров до проверки значений."""
    missing = FIELDS - data.keys()
    extra = data.keys() - FIELDS
    if missing or extra:
        raise AppError(f"Поля TOML: отсутствуют {sorted(missing)}; "
                       f"неизвестны {sorted(extra)}")
    for key in FIELDS - {"test_mode", "max_depth"}:
        if not isinstance(data[key], str):
            raise AppError(f"{key}: требуется строка")
    if type(data["test_mode"]) is not bool:
        raise AppError("test_mode: требуется true или false")
    depth = data["max_depth"]
    if type(depth) is not int or not 0 <= depth <= MAX_DEPTH:
        raise AppError(f"max_depth: целое число от 0 до {MAX_DEPTH}")


def validate_values(data, folder):
    """Проверить имя, версию, URL либо путь и строку фильтра."""
    pattern = r"[A-Z]+" if data["test_mode"] else PACKAGE
    if not re.fullmatch(pattern, data["package"]):
        raise AppError("package: неверное имя пакета")
    if not re.fullmatch(VERSION, data["version"]):
        raise AppError("version: требуется точная версия, например 1.0.0")
    if any(ord(char) < 32 for char in data["filter_substring"]):
        raise AppError("filter_substring: управляющие символы запрещены")
    if data["test_mode"]:
        path = folder / data["repository"]
        if not data["repository"] or not path.is_file():
            raise AppError("repository: тестовый файл не найден")
        data["repository"] = str(path.resolve())
    else:
        validate_url(data["repository"])


def validate_url(value):
    """Допустить HTTP(S)-реестр без учётных данных и параметров URL."""
    try:
        url = urlsplit(value)
        valid = (url.scheme in {"http", "https"} and url.hostname
                 and not url.username and not url.query and not url.fragment)
        port = url.port
    except ValueError as exc:
        raise AppError("repository: неверный URL") from exc
    if not valid or port == 0:
        raise AppError("repository: требуется HTTP(S) URL реестра npm")


def load_config(path):
    """Загрузить TOML; относительный путь считать от файла конфигурации."""
    path = Path(path)
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, ValueError) as exc:
        raise AppError(f"Не удалось прочитать TOML: {exc}") from exc
    validate_fields(data)
    validate_values(data, path.resolve().parent)
    return Config(**data)
