"""Первый этап: простой парсер и команды-заглушки."""

import getpass
import socket

from .errors import EmulatorError

MAX_CD_ARGS = 1
MAX_LS_ARGS = 2


class ShellEmulator:
    """Прототип оболочки с командами ls, cd и exit."""

    def __init__(self, vfs, prompt="$ "):
        """Подготовить состояние графического REPL."""
        self.vfs = vfs
        self.prompt = prompt
        self.should_exit = False

    @property
    def window_title(self):
        """Использовать реальные имя пользователя и имя компьютера."""
        return f"Эмулятор - [{getpass.getuser()}@{socket.gethostname()}]"

    def execute(self, line):
        """Разделить ввод и вызвать заглушку или команду завершения."""
        parts = line.strip().split()
        if not parts:
            return ""
        command, args = parts[0], parts[1:]
        if command == "exit":
            if args:
                raise EmulatorError("exit: команда не принимает аргументы")
            self.should_exit = True
            return ""
        if command not in {"ls", "cd"}:
            raise EmulatorError(f"{command}: неизвестная команда")
        self._check_args(command, args)
        return f"{command}: {' '.join(args)}"

    def _check_args(self, command, args):
        """Проверить аргументы заглушек до реализации VFS."""
        limit = MAX_CD_ARGS if command == "cd" else MAX_LS_ARGS
        if len(args) > limit:
            raise EmulatorError(f"{command}: слишком много аргументов")
        if command == "ls":
            for arg in args:
                if arg.startswith("-") and arg != "-l":
                    raise EmulatorError(f"ls: неизвестный параметр: {arg}")
