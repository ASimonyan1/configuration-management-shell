"""Точка входа: python -m src.main из корня репозитория."""

import sys
import tkinter as tk

from .config import parse_args, resolve_config
from .errors import EmulatorError
from .gui import EmulatorGUI
from .shell import ShellEmulator
from .vfs import VirtualFileSystem


def build_shell(args):
    """Проверить настройки и загрузить VFS до открытия окна."""
    config = resolve_config(args)
    if not config.vfs:
        raise EmulatorError("Не задан VFS: используйте --vfs или --config")
    vfs = VirtualFileSystem()
    vfs.load_csv(config.vfs)
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
