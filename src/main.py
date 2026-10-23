"""Командная строка практики 2, вариант 26."""

import argparse
import sys

from .config import load_config
from .errors import AppError
from .registry import Registry


def arguments(argv):
    """Прочитать путь TOML и параметры вывода текущего этапа."""
    parser = argparse.ArgumentParser(description="Практика 2, вариант 26")
    parser.add_argument("--config", default="config.toml")

    return parser.parse_args(argv)


def execute(args):
    """Выполнить функциональность только текущего этапа."""
    config = load_config(args.config)
    if config.test_mode:
        raise AppError("Тестовый источник реализуется на этапе 3")
    repo = Registry(config.repository)
    deps = repo.dependencies(config.package, config.version)
    for name, version in sorted(deps.items()):
        print(f"{name}: {version}")
    if not deps:
        print("Прямых зависимостей нет")


def main(argv=None):
    """Запустить приложение; вывести понятную ошибку без traceback."""
    args = arguments(argv)
    try:
        execute(args)
    except (AppError, OSError, RecursionError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
