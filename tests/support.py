"""Временные файлы для изолированных проверок."""

import tempfile
import unittest
from pathlib import Path


class TempCase(unittest.TestCase):
    """Создавать временную папку для каждого теста."""

    def setUp(self):
        """Выделить независимую папку и зарегистрировать очистку."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def write_file(self, text, name="input.txt"):
        """Записать UTF-8 фикстуру и вернуть путь."""
        path = self.folder / name
        path.write_text(text, encoding="utf-8", newline="")
        return path
