"""Командная строка практики 2, вариант 26."""

import argparse
import sys

from .config import load_config
from .errors import AppError
from .registry import Registry
from .test_repository import TestRepository
from .graph import Builder, graph_text, label
from .reverse import reverse_dependencies


def arguments(argv):
    """Прочитать путь TOML и параметры вывода текущего этапа."""
    parser = argparse.ArgumentParser(description="Практика 2, вариант 26")
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--reverse-target")
    return parser.parse_args(argv)


def execute(args):
    """Выполнить функциональность только текущего этапа."""
    config = load_config(args.config)
    repo = (TestRepository(config.repository) if config.test_mode
            else Registry(config.repository))
    graph = Builder(repo, config).build()
    target = args.reverse_target or config.package
    parents = reverse_dependencies(graph, target)
    print(f"Обратные зависимости {target} в исследованном графе:")
    print("\n".join(label(node) for node in sorted(parents)) or "Нет")


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
