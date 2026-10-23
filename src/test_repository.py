"""JSON-репозиторий с пакетами, названными заглавными латинскими буквами."""

import json
import re
from pathlib import Path

from .errors import AppError
from .registry import dependencies_of
from .versions import select_version


class TestRepository:
    """Локальный реестр: имя -> версия -> dependencies."""

    def __init__(self, path):
        """Прочитать и проверить весь локальный репозиторий."""
        try:
            self.packages = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise AppError(f"Ошибка тестового репозитория: {exc}") from exc
        self.validate()

    def validate(self):
        """Проверить узлы, версии и все ссылки между пакетами."""
        if not isinstance(self.packages, dict) or not self.packages:
            raise AppError("Тестовый репозиторий должен быть непустым объектом")
        for name, versions in self.packages.items():
            if not re.fullmatch(r"[A-Z]+", name):
                raise AppError(f"Тестовое имя должно состоять из A-Z: {name}")
            if not isinstance(versions, dict) or not versions:
                raise AppError(f"Нет версий пакета {name}")
            for version, metadata in versions.items():
                self.validate_version(version, metadata)

    def validate_version(self, version, metadata):
        """Проверить запись версии и разрешимость её зависимостей."""
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise AppError(f"Неверная тестовая версия: {version}")
        if not isinstance(metadata, dict):
            raise AppError("Описание версии должно быть объектом")
        for child, expression in dependencies_of(metadata).items():
            self.resolve(child, expression)

    def resolve(self, name, expression):
        """Разрешить диапазон в локальном репозитории."""
        versions = self.packages.get(name)
        if not isinstance(versions, dict) or not versions:
            raise AppError(f"Нет пакета в тестовом репозитории: {name}")
        return name, select_version(versions, expression)

    def dependencies(self, name, version):
        """Прочитать прямые зависимости конкретной версии."""
        metadata = self.packages.get(name, {}).get(version)
        if not isinstance(metadata, dict):
            raise AppError(f"Нет тестовой версии {name}@{version}")
        return dependencies_of(metadata)
