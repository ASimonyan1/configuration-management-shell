"""Парсер и команды оболочки, предусмотренные вариантом №26."""

import getpass
import posixpath
import socket

from .errors import EmulatorError

NO_ARGS = 0
ONE_ARG = 1
OWNER_PATH_ARGS = 2
DEFAULT_TAIL_COUNT = 10
MIN_TAIL_COUNT = 0


def require_count(args, expected, usage):
    """Проверить число аргументов команды и показать её синтаксис."""
    if len(args) != expected:
        raise EmulatorError(usage)


def parse_ls(args):
    """Разобрать ls с необязательными -l и одним путём."""
    long_mode = False
    path = None
    for arg in args:
        if arg == "-l":
            if long_mode:
                raise EmulatorError("ls: параметр -l указан повторно")
            long_mode = True
        elif arg.startswith("-"):
            raise EmulatorError(f"ls: неизвестный параметр: {arg}")
        elif path is not None:
            raise EmulatorError("ls: можно указать только один путь")
        else:
            path = arg
    return long_mode, "." if path is None else path






def format_node(node, long_mode):
    """Сформировать краткую или подробную строку ls."""
    name = posixpath.basename(node.path) or "/"
    if node.kind == "dir" and name != "/":
        name += "/"
    if not long_mode:
        return name
    kind = "d" if node.kind == "dir" else "-"
    return f"{kind} {node.owner:<12} {len(node.content):>6} {name}"


class ShellEmulator:
    """Состояние оболочки, реальные имя пользователя и имя компьютера."""

    def __init__(self, vfs, prompt="$ "):
        """Подключить VFS и подготовить состояние сеанса."""
        self.vfs = vfs
        self.prompt = prompt
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.should_exit = False

    @property
    def window_title(self):
        """Получить заголовок GUI на основе данных реальной ОС."""
        return f"Эмулятор - [{self.username}@{self.hostname}]"

    def execute(self, line):
        """Разделить ввод по пробелам и выполнить указанную команду."""
        parts = line.strip().split()
        if not parts:
            return ""
        handlers = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
        }
        handler = handlers.get(parts[0])
        if handler is None:
            raise EmulatorError(f"{parts[0]}: неизвестная команда")
        return handler(parts[1:])

    def _cmd_ls(self, args):
        """Показать содержимое каталога или сведения об одном файле."""
        long_mode, path = parse_ls(args)
        return "\n".join(
            format_node(node, long_mode) for node in self.vfs.list_dir(path)
        )

    def _cmd_cd(self, args):
        """Перейти по пути; без аргументов перейти в корень VFS."""
        if len(args) > ONE_ARG:
            raise EmulatorError("cd: слишком много аргументов")
        self.vfs.change_dir(args[0] if args else "/")
        return ""





    def _cmd_exit(self, args):
        """Запросить закрытие GUI, проверив отсутствие аргументов."""
        require_count(args, NO_ARGS, "exit: команда не принимает аргументы")
        self.should_exit = True
        return ""
