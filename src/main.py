"""Запуск минимального графического REPL, этап 1."""

import tkinter as tk
from types import SimpleNamespace

from .gui import EmulatorGUI
from .shell import ShellEmulator


def main():
    """Открыть окно с заглушками ls/cd и обработчиком exit."""
    root = tk.Tk()
    EmulatorGUI(root, ShellEmulator(SimpleNamespace(cwd="/")))
    root.mainloop()


if __name__ == "__main__":
    main()
