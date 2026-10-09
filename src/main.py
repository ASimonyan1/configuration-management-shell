"""Запуск второго этапа: python -m src.main с параметрами."""

import sys
import tkinter as tk

from .config import parse_args, resolve_config
from .errors import EmulatorError
from .gui import EmulatorGUI
from .shell import ShellEmulator


def build_shell(args):
    """Применить конфигурацию; путь VFS пока только отображается."""
    config = resolve_config(args)
    prompt = "$ " if config.prompt is None else config.prompt
    return ShellEmulator(prompt), config


def main(argv=None):
    """Открыть REPL или вернуть код 2 при ошибке настроек и окна."""
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
