"""Командная строка практики 2, вариант 26."""

import argparse
import sys

from .config import load_config
from .errors import AppError
from .registry import Registry
from .test_repository import TestRepository
from .graph import Builder
from .visualize import render


def arguments(argv):
    """Прочитать путь TOML и параметры вывода текущего этапа."""
    parser = argparse.ArgumentParser(description="Практика 2, вариант 26")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--output", default="output/graph")
    parser.add_argument("--no-open", action="store_true")
    return parser.parse_args(argv)


def execute(args):
    """Выполнить функциональность только текущего этапа."""
    config = load_config(args.config)
    repo = (TestRepository(config.repository) if config.test_mode
            else Registry(config.repository))
    graph = Builder(repo, config).build()
    path = render(graph, args.output, show=not args.no_open)
    print(f"Изображение: {path}")


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
