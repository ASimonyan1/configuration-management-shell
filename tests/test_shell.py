"""Функциональные проверки всех команд и неверных аргументов."""

import getpass
import socket

from src.errors import EmulatorError
from src.shell import ShellEmulator
from src.vfs import VirtualFileSystem
from tests.support import CSV, TempCase


class ShellTests(TempCase):
    """Проверить реальные результаты команд на изолированной VFS."""

    def setUp(self):
        """Создать оболочку и сохранить путь к исходному CSV."""
        super().setUp()
        self.path = self.write_file(CSV, "vfs.csv")
        vfs = VirtualFileSystem()
        vfs.load_csv(self.path)
        self.shell = ShellEmulator(vfs, "test> ")

    def test_ls_cd_and_space_parser(self):
        """Команды понимают пробелы, пути, подробный и краткий вывод."""
        self.assertEqual(self.shell.execute("   \t"), "")
        self.assertIn("home/", self.shell.execute("  ls   /  "))
        self.shell.execute("cd /home/u")
        self.assertIn("a.txt", self.shell.execute("ls -l ."))
        self.assertEqual(self.shell.execute("ls a.txt"), "a.txt")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.vfs.cwd, "/home")
        self.shell.execute("cd")
        self.assertEqual(self.shell.vfs.cwd, "/")

    def test_rev_and_tail_modes(self):
        """rev и каждый режим tail дают ожидаемый текст."""
        self.shell.execute("cd /home/u")
        self.assertEqual(self.shell.execute("rev a.txt"), "cba\nfed\nihg")
        for command, expected in (
            ("tail a.txt", "abc\ndef\nghi"),
            ("tail -n 2 a.txt", "def\nghi"),
            ("tail -2 a.txt", "def\nghi"),
            ("tail a.txt -n 1", "ghi"),
            ("tail -n 0 a.txt", ""),
            ("tail -99 a.txt", "abc\ndef\nghi"),
        ):
            with self.subTest(command=command):
                self.assertEqual(self.shell.execute(command), expected)

    def test_tail_default_is_ten_lines(self):
        """По умолчанию tail возвращает именно последние десять строк."""
        self.shell.vfs.get("/home/u/a.txt").content = (
            b"1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12"
        )
        self.assertEqual(
            self.shell.execute("tail /home/u/a.txt"),
            "3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
        )

    def test_who_title_and_exit(self):
        """who и заголовок используют ОС, exit меняет состояние сеанса."""
        expected = f"{getpass.getuser()}@{socket.gethostname()}"
        self.assertIn(expected, self.shell.window_title)
        self.assertEqual(
            self.shell.execute("who"),
            f"{getpass.getuser()}\t{socket.gethostname()}\t/",
        )
        self.assertEqual(self.shell.execute("exit"), "")
        self.assertTrue(self.shell.should_exit)

    def test_invalid_arguments_and_paths(self):
        """Команды не принимают лишние аргументы, флаги и неверные пути."""
        commands = (
            "unknown", "ls . /", "ls -l -l", "ls -z", "ls /missing",
            "cd / /home", "cd /binary", "cd /missing", "rev", "rev / /",
            "rev /missing", "rev /home", "rev /binary", "tail", "tail -n",
            "tail -n x /home/u/a.txt", "tail -n -1 /home/u/a.txt",
            "tail -z /home/u/a.txt", "tail /home/u/a.txt /home/u/a.txt",
            "tail /missing", "tail /binary", "tail /home", "who x", "exit x",
        )
        for command in commands:
            with self.subTest(command=command):
                with self.assertRaises(EmulatorError):
                    self.shell.execute(command)
        self.assertFalse(self.shell.should_exit)
