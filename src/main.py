"""Запуск первого этапа: python -m src.main, без параметров."""

import sys
import tkinter as tk

from .gui import EmulatorGUI
from .shell import ShellEmulator


def main():
    """Создать графический REPL с заглушками ls/cd и командой exit."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"Не удалось открыть окно: {exc}", file=sys.stderr)
        return 1
    EmulatorGUI(root, ShellEmulator())
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
