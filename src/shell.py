"""Этап 1 варианта №26: парсер, заглушки ls/cd и завершение."""

import getpass
import socket

from .errors import EmulatorError

MAX_CD_ARGS = 1
MAX_LS_PATHS = 1


def validate_ls(args):
    """Разрешить один путь и один необязательный флаг -l."""
    paths = []
    long_mode = False
    for arg in args:
        if arg == "-l":
            if long_mode:
                raise EmulatorError("ls: параметр -l указан повторно")
            long_mode = True
        elif arg.startswith("-"):
            raise EmulatorError(f"ls: неизвестный параметр: {arg}")
        else:
            paths.append(arg)
    if len(paths) > MAX_LS_PATHS:
        raise EmulatorError("ls: использование: ls [-l] [ПУТЬ]")


def validate_cd(args):
    """Разрешить не более одного пути без дополнительных флагов."""
    if len(args) > MAX_CD_ARGS:
        raise EmulatorError("cd: использование: cd [ПУТЬ]")
    if args and args[0].startswith("-"):
        raise EmulatorError(f"cd: неизвестный параметр: {args[0]}")


def stub_output(command, args):
    """Вывести имя команды и разобранные аргументы, не выполняя команду."""
    return f"Команда: {command}\nАргументы: {args!r}"


class ShellEmulator:
    """Состояние минимального REPL без файловой системы и конфигурации."""

    def __init__(self):
        """Подготовить постоянное приглашение и флаг завершения."""
        self.prompt = "$ "
        self.should_exit = False

    @property
    def window_title(self):
        """Сформировать заголовок из реальных данных операционной системы."""
        return f"Эмулятор - [{getpass.getuser()}@{socket.gethostname()}]"

    def execute(self, line):
        """Разбить ввод по пробельным символам и выбрать обработчик."""
        parts = line.split()
        if not parts:
            return ""
        command, args = parts[0], parts[1:]
        handlers = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
        }
        if command not in handlers:
            raise EmulatorError(f"{command}: неизвестная команда")
        return handlers[command](args)

    def _cmd_ls(self, args):
        """Проверить аргументы ls и вывести результат заглушки."""
        validate_ls(args)
        return stub_output("ls", args)

    def _cmd_cd(self, args):
        """Проверить аргументы cd и вывести результат заглушки."""
        validate_cd(args)
        return stub_output("cd", args)

    def _cmd_exit(self, args):
        """Запросить закрытие окна только при отсутствии аргументов."""
        if args:
            raise EmulatorError("exit: команда не принимает аргументы")
        self.should_exit = True
        return ""
