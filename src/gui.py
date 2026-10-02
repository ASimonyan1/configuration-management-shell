"""Графический REPL и последовательное выполнение стартового сценария."""

import tkinter as tk
from tkinter import ttk

from .config import iter_script_commands
from .errors import EmulatorError

SCRIPT_DELAY_MS = 120
EXIT_DELAY_MS = 100


class EmulatorGUI:
    """Окно с журналом диалога и полем ввода команд."""

    def __init__(self, root, shell):
        """Создать окно и подключить обработчик ввода."""
        self.root = root
        self.shell = shell
        root.title(shell.window_title)
        root.geometry("900x600")
        root.minsize(700, 450)
        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)
        self._create_output(frame)
        self._create_input(frame)
        self.append(
            f"{shell.window_title}\nТекущий каталог VFS: {shell.vfs.cwd}\n\n"
        )

    def _create_output(self, frame):
        """Добавить защищённый от редактирования журнал диалога."""
        self.output = tk.Text(
            frame, wrap="word", state="disabled", font=("Consolas", 11)
        )
        self.output.pack(fill="both", expand=True, pady=(0, 8))

    def _create_input(self, frame):
        """Добавить приглашение, поле ввода и обработчик Enter."""
        row = ttk.Frame(frame)
        row.pack(fill="x")
        ttk.Label(row, text=self.shell.prompt).pack(side="left")
        self.entry = ttk.Entry(row)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def append(self, text):
        """Добавить текст в журнал и прокрутить к последней строке."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def run_command(self, line):
        """Показать ввод, результат или ошибку; обработать завершение."""
        self.append(f"{self.shell.prompt}{line}\n")
        try:
            result = self.shell.execute(line)
            if result:
                self.append(result + "\n")
        except EmulatorError as exc:
            self.append(f"Ошибка: {exc}\n")
        if self.shell.should_exit:
            self.root.after(EXIT_DELAY_MS, self.root.destroy)

    def _on_enter(self, _event=None):
        """Передать введённую пользователем строку эмулятору."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.run_command(line)

    def show_config(self, config, config_path):
        """Вывести итоговые значения всех четырёх параметров запуска."""
        self.append(
            "Параметры запуска:\n"
            f"VFS: {config.vfs}\nPrompt: {self.shell.prompt}\n"
            f"Script: {config.script or 'не задан'}\n"
            f"Config: {config_path or 'не задан'}\n\n"
        )

    def start_script(self, path):
        """Загрузить сценарий; при ошибке оставить интерактивный REPL."""
        if not path:
            return
        try:
            commands = iter(list(iter_script_commands(path)))
        except EmulatorError as exc:
            self.append(f"Ошибка: {exc}\n")
            return
        self.root.after(SCRIPT_DELAY_MS, lambda: self._script_step(commands))

    def _script_step(self, commands):
        """Выполнить одну команду сценария без блокирования GUI."""
        if self.shell.should_exit:
            return
        line = next(commands, None)
        if line is None:
            return
        self.run_command(line)
        if not self.shell.should_exit:
            self.root.after(
                SCRIPT_DELAY_MS, lambda: self._script_step(commands)
            )
