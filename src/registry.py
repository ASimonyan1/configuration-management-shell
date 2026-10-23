"""Получение npm-метаданных через стандартную библиотеку urllib."""

import json
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .errors import AppError
from .versions import select_version

TIMEOUT = 20
MAX_RESPONSE = 30 * 1024 * 1024


def read_json(url):
    """Прочитать ограниченный по размеру ответ HTTP и разобрать JSON."""
    request = Request(url, headers={
        "Accept": "application/vnd.npm.install-v1+json",
        "User-Agent": "variant26-dependency-viewer/1.0",
    })
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            data = response.read(MAX_RESPONSE + 1)
        if len(data) > MAX_RESPONSE:
            raise AppError("Ответ реестра слишком большой")
        result = json.loads(data)
    except (URLError, OSError, ValueError) as exc:
        raise AppError(f"Ошибка реестра {url}: {exc}") from exc
    if not isinstance(result, dict):
        raise AppError("Реестр должен вернуть объект JSON")
    return result


def dependencies_of(metadata):
    """Прочитать runtime-зависимости; dev/peer/optional не анализируются."""
    dependencies = metadata.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise AppError("dependencies должен быть объектом")
    for name, version in dependencies.items():
        if not isinstance(name, str) or not isinstance(version, str):
            raise AppError("Имя и диапазон зависимости должны быть строками")
        if not name or not version:
            raise AppError("Пустое имя или диапазон зависимости")
    return dependencies


class Registry:
    """Реестр npm с кэшем метаданных в памяти на время анализа."""

    def __init__(self, url):
        """Сохранить адрес реестра и создать кэш."""
        self.url = url.rstrip("/")
        self.cache = {}

    def package(self, name):
        """Загрузить все версии одного пакета, включая scoped-имена."""
        if name not in self.cache:
            self.cache[name] = read_json(self.url + "/" + quote(name, safe=""))
        result = self.cache[name]
        if not isinstance(result.get("versions"), dict):
            raise AppError(f"У пакета {name} нет списка versions")
        return result

    def resolve(self, name, expression):
        """Найти точную версию зависимости по её диапазону."""
        package = self.package(name)
        version = select_version(package["versions"], expression,
                                 package.get("dist-tags", {}))
        return name, version

    def dependencies(self, name, version):
        """Получить прямые зависимости именно запрошенной версии."""
        metadata = self.package(name)["versions"].get(version)
        if not isinstance(metadata, dict):
            raise AppError(f"Не найдена версия {name}@{version}")
        return dependencies_of(metadata)
