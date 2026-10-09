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


def parse_count(value):
    """Преобразовать количество строк tail в неотрицательное число."""
    try:
        count = int(value)
    except ValueError as exc:
        raise EmulatorError("tail: N должно быть целым числом") from exc
    if count < MIN_TAIL_COUNT:
        raise EmulatorError("tail: N не может быть отрицательным")
    return count


def parse_tail(args):
    """Разобрать tail ФАЙЛ, tail -n N ФАЙЛ и tail -N ФАЙЛ."""
    count = DEFAULT_TAIL_COUNT
    path = None
    tokens = iter(args)
    for arg in tokens:
        if arg == "-n":
            value = next(tokens, None)
            if value is None:
                raise EmulatorError("tail: после -n требуется число")
            count = parse_count(value)
        elif arg.startswith("-") and arg[1:].isdigit():
            count = parse_count(arg[1:])
        elif arg.startswith("-"):
            raise EmulatorError(f"tail: неизвестный параметр: {arg}")
        elif path is not None:
            raise EmulatorError("tail: можно указать только один файл")
        else:
            path = arg
    if path is None:
        raise EmulatorError("tail: использование: tail [-n N | -N] ФАЙЛ")
    return count, path


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
            "rev": self._cmd_rev,
            "tail": self._cmd_tail,
            "who": self._cmd_who,
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

    def _cmd_rev(self, args):
        """Развернуть символы отдельно в каждой строке текстового файла."""
        require_count(args, ONE_ARG, "rev: использование: rev ФАЙЛ")
        return "\n".join(
            line[::-1] for line in self.vfs.read_text(args[0]).splitlines()
        )

    def _cmd_tail(self, args):
        """Показать последние N строк; значение по умолчанию равно десяти."""
        count, path = parse_tail(args)
        lines = self.vfs.read_text(path).splitlines()
        return "\n".join(lines[-count:]) if count else ""

    def _cmd_who(self, args):
        """Показать пользователя, компьютер и текущий каталог эмулятора."""
        require_count(args, NO_ARGS, "who: команда не принимает аргументы")
        return f"{self.username}\t{self.hostname}\t{self.vfs.cwd}"


    def _cmd_exit(self, args):
        """Запросить закрытие GUI, проверив отсутствие аргументов."""
        require_count(args, NO_ARGS, "exit: команда не принимает аргументы")
        self.should_exit = True
        return ""
