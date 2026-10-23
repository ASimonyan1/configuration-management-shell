"""Ошибки всех шести параметров и чтения TOML."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config
from src.errors import AppError

VALID = '''package = "is-odd"
repository = "https://registry.npmjs.org"
test_mode = false
version = "3.0.1"
max_depth = 5
filter_substring = ""
'''


class ConfigTests(unittest.TestCase):
    """Проверить валидную конфигурацию и ошибки каждого поля."""

    def setUp(self):
        """Подготовить временный каталог теста."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "config.toml"

    def write(self, text):
        """Записать TOML для текущего теста."""
        self.path.write_text(text, encoding="utf-8")
        return self.path

    def test_valid_and_zero_depth(self):
        """Верные значения и нулевая глубина принимаются."""
        config = load_config(self.write(VALID.replace('= 5', '= 0')))
        self.assertEqual(config.package, "is-odd")
        self.assertEqual(config.max_depth, 0)

    def test_all_invalid_parameters(self):
        """Каждый неверный параметр выдаёт пользовательскую ошибку."""
        replacements = [
            ('"is-odd"', '"bad name"'),
            ('"https://registry.npmjs.org"', '"file:///tmp"'),
            ('false', '"false"'), ('"3.0.1"', '"latest"'),
            ('= 5', '= -1'), ('= 5', '= true'),
            ('filter_substring = ""', 'filter_substring = 7'),
            ('filter_substring = ""', 'filter_substring = "\\n"'),
        ]
        for old, new in replacements:
            with self.subTest(new=new), self.assertRaises(AppError):
                load_config(self.write(VALID.replace(old, new)))

    def test_missing_unknown_and_broken_toml(self):
        """Отсутствующие, лишние поля и синтаксис TOML проверяются."""
        samples = ['[', VALID + 'unknown = 1\n',
                   VALID.replace('version = "3.0.1"\n', '')]
        for text in samples:
            with self.subTest(text=text), self.assertRaises(AppError):
                load_config(self.write(text))
        with self.assertRaises(AppError):
            load_config(self.path.with_name("missing.toml"))

    def test_test_path_relative_to_config(self):
        """Тестовый путь считается от TOML, а не рабочего каталога."""
        (self.path.parent / "repo.json").write_text("{}", encoding="utf-8")
        text = VALID.replace('"is-odd"', '"A"').replace('false', 'true')
        text = text.replace('https://registry.npmjs.org', 'repo.json')
        config = load_config(self.write(text))
        self.assertTrue(Path(config.repository).is_absolute())
        with self.assertRaises(AppError):
            load_config(self.write(text.replace('repo.json', 'absent.json')))
