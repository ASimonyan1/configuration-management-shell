"""Изолированные временные файлы для тестов."""

import tempfile
import unittest
from pathlib import Path

HEADER = "path,type,content,encoding,owner\n"
CSV = HEADER + '''/home/u/a.txt,file,"abc
def
ghi",text,u
/home/u/deep/level/f.txt,file,hello,text,u
/empty,dir,,text,root
/binary,file,AAEC,base64,root
'''


class TempCase(unittest.TestCase):
    """Создавать и удалять временную папку для каждого теста."""

    def setUp(self):
        """Выделить независимую папку и зарегистрировать её очистку."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def write_file(self, text, name="input.txt"):
        """Записать UTF-8 фикстуру и вернуть путь."""
        path = self.folder / name
        path.write_text(text, encoding="utf-8", newline="")
        return path
