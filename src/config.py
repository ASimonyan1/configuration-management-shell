"""Аргументы запуска, JSON-конфигурация и стартовые сценарии."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .errors import EmulatorError


@dataclass
class AppConfig:
    """Пути VFS и сценария, приглашение командной строки."""

    vfs: str | None = None
    prompt: str | None = None
    script: str | None = None


def parse_args(argv=None):
    """Прочитать четыре поддерживаемых параметра командной строки."""
    parser = argparse.ArgumentParser(
        description="GUI-эмулятор UNIX-подобной оболочки, вариант №26"
    )
    parser.add_argument("--vfs", help="CSV-файл виртуальной файловой системы")
    parser.add_argument("--prompt", help="Приглашение к вводу")
    parser.add_argument("--script", help="Стартовый сценарий команд")
    parser.add_argument("--config", help="JSON-конфигурация")
    return parser.parse_args(argv)


def load_json_config(path):
    """Прочитать JSON и проверить типы значений настроек."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise EmulatorError(f"Конфигурация: ошибка чтения: {exc}") from exc
    if not isinstance(data, dict):
        raise EmulatorError("Конфигурация: корнем JSON должен быть объект")
    for key in ("vfs", "prompt", "script"):
        value = data.get(key)
        if value is not None and not isinstance(value, str):
            raise EmulatorError(f"Конфигурация: {key} должен быть строкой")
    return AppConfig(data.get("vfs"), data.get("prompt"), data.get("script"))


def merge_config(file_config, cli_vfs, cli_prompt, cli_script):
    """Применить значения CLI поверх JSON, сохранив пустые строки CLI."""
    return AppConfig(
        vfs=file_config.vfs if cli_vfs is None else cli_vfs,
        prompt=file_config.prompt if cli_prompt is None else cli_prompt,
        script=file_config.script if cli_script is None else cli_script,
    )


def resolve_config(args):
    """Собрать итоговую конфигурацию с приоритетом аргументов CLI."""
    config = load_json_config(args.config) if args.config else AppConfig()
    return merge_config(config, args.vfs, args.prompt, args.script)


def iter_script_commands(path):
    """Читать непустые строки, пропуская комментарии с символом #."""
    try:
        lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EmulatorError(f"Стартовый скрипт: ошибка чтения: {exc}") from exc
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield line
