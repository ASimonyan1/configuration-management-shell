"""Командная строка практики 2, вариант 26."""

import argparse
import sys

from .config import load_config
from .errors import AppError
from dataclasses import asdict


def arguments(argv):
    """Прочитать путь TOML и параметры вывода текущего этапа."""
    parser = argparse.ArgumentParser(description="Практика 2, вариант 26")
    parser.add_argument("--config", default="config.toml")

    return parser.parse_args(argv)


def execute(args):
    """Выполнить функциональность только текущего этапа."""
    config = load_config(args.config)
    for key, value in asdict(config).items():
        print(f"{key} = {value}")


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
