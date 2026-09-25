"""Проверки CSV, вложенности и ограничений виртуальной файловой системы."""

from src.errors import EmulatorError
from src.vfs import VirtualFileSystem
from tests.support import CSV, HEADER, TempCase


class VFSTests(TempCase):
    """Проверить загрузку и работу с VFS без изменения источника."""

    def setUp(self):
        """Загрузить отдельную VFS для каждого теста."""
        super().setUp()
        self.path = self.write_file(CSV, "vfs.csv")
        self.vfs = VirtualFileSystem()
        self.vfs.load_csv(self.path)

    def test_nested_relative_and_root_paths(self):
        """Создаются родители, работают относительные пути и корень."""
        self.vfs.change_dir("/home/u/deep/level")
        self.assertTrue(self.vfs.exists("f.txt"))
        self.assertEqual(self.vfs.resolve("../../a.txt"), "/home/u/a.txt")
        self.assertEqual(self.vfs.resolve("../../../../../../"), "/")
        self.assertEqual(self.vfs.resolve("//home"), "/home")

    def test_binary_decoding_and_text_restriction(self):
        """Base64 декодируется в памяти, текстовые операции его отклоняют."""
        self.assertEqual(self.vfs.get("/binary").content, b"\x00\x01\x02")
        with self.assertRaises(EmulatorError):
            self.vfs.read_text("/binary")

    def test_list_file_empty_directory_and_order(self):
        """Файлы, пустые каталоги и порядок ls обрабатываются отдельно."""
        self.assertEqual(self.vfs.list_dir("/empty"), [])
        self.assertEqual(self.vfs.list_dir("/binary")[0].path, "/binary")
        self.assertEqual(self.vfs.list_dir("/")[0].path, "/empty")

    def test_invalid_csv_does_not_replace_existing_vfs(self):
        """Неверные заголовки, узлы и base64 не портят загруженные данные."""
        invalid = (
            "wrong\nheader\n",
            HEADER + ",file,x,text,u\n",
            HEADER + "/x,wrong,x,text,u\n",
            HEADER + "/x,file,x,wrong,u\n",
            HEADER + "/x,file,@@,base64,u\n",
            HEADER + "/x,file,x,text,u\n/x,file,y,text,u\n",
            HEADER + "/x,file,x,text,u\n/x/y,file,y,text,u\n",
            HEADER + "/,file,x,text,u\n",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(EmulatorError):
                self.vfs.load_csv(self.write_file(text))
            self.assertTrue(self.vfs.exists("/home/u/a.txt"))

    def test_missing_file_and_invalid_utf8(self):
        """Ошибки файловой системы и декодирования обрабатываются."""
        with self.assertRaises(EmulatorError):
            self.vfs.load_csv(self.folder / "missing.csv")
        path = self.folder / "bad.csv"
        path.write_bytes(b"\xff")
        with self.assertRaises(EmulatorError):
            self.vfs.load_csv(path)

    def test_directory_and_missing_path_errors(self):
        """Нельзя читать каталог как текст или переходить в файл."""
        for action, path in (
            (self.vfs.read_text, "/home"),
            (self.vfs.change_dir, "/binary"),
            (self.vfs.get, "/missing"),
        ):
            with self.subTest(path=path), self.assertRaises(EmulatorError):
                action(path)

    def test_operations_continue_after_source_is_removed(self):
        """После загрузки ls, cd и чтение не обращаются к CSV."""
        self.path.unlink()
        self.vfs.change_dir("/home/u")
        self.assertEqual(self.vfs.read_text("a.txt"), "abc\ndef\nghi")
        self.assertTrue(self.vfs.list_dir())
