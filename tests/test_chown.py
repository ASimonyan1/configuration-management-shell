"""Проверки изменения владельца исключительно в оперативной памяти."""

from src.errors import EmulatorError
from src.shell import ShellEmulator
from src.vfs import VirtualFileSystem
from tests.support import CSV, TempCase


class ChownTests(TempCase):
    """Проверить файлы, каталоги, ошибки и неизменность исходного CSV."""

    def setUp(self):
        """Создать независимую оболочку и исходный файл."""
        super().setUp()
        self.path = self.write_file(CSV, "vfs.csv")
        vfs = VirtualFileSystem()
        vfs.load_csv(self.path)
        self.shell = ShellEmulator(vfs)

    def test_file_directory_and_source_unchanged(self):
        """chown меняет память; загрузка восстанавливает владельца."""
        before = self.path.read_bytes()
        self.shell.execute("chown teacher /home/u/a.txt")
        self.shell.execute("chown admin /home/u")
        self.assertEqual(self.shell.vfs.get("/home/u/a.txt").owner, "teacher")
        self.assertEqual(self.shell.vfs.get("/home/u").owner, "admin")
        self.assertEqual(self.path.read_bytes(), before)
        self.shell.vfs.load_csv(self.path)
        self.assertEqual(self.shell.vfs.get("/home/u/a.txt").owner, "u")

    def test_invalid_chown(self):
        """Нужны ровно два аргумента и существующий путь."""
        for command in ("chown", "chown user", "chown u / x", "chown u /x"):
            with self.subTest(command=command):
                with self.assertRaises(EmulatorError):
                    self.shell.execute(command)
        with self.assertRaises(EmulatorError):
            self.shell.vfs.chown("", "/home")
