"""Точка входа: python -m src.main из корня репозитория."""

import sys
import tkinter as tk

from .config import parse_args, resolve_config
from .errors import EmulatorError
from .gui import EmulatorGUI
from .shell import ShellEmulator
from types import SimpleNamespace


def build_shell(args):
    """Прочитать настройки; подключение VFS появится на этапе 3."""
    config = resolve_config(args)
    if not config.vfs:
        raise EmulatorError("Не задан VFS: используйте --vfs или --config")
    vfs = SimpleNamespace(cwd="/")
    prompt = "$ " if config.prompt is None else config.prompt
    return ShellEmulator(vfs, prompt), config


def main(argv=None):
    """Запустить GUI; вернуть код 2 при ошибке запуска."""
    args = parse_args(argv)
    try:
        shell, config = build_shell(args)
        root = tk.Tk()
    except (EmulatorError, tk.TclError) as exc:
        print(f"Ошибка запуска: {exc}", file=sys.stderr)
        return 2
    gui = EmulatorGUI(root, shell)
    gui.show_config(config, args.config)
    gui.start_script(config.script)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
