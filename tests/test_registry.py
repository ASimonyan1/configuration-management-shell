"""Проверки HTTP, точной версии и самостоятельного SemVer."""

import unittest
from unittest.mock import MagicMock, patch

from src.errors import AppError
from src.registry import Registry, dependencies_of, read_json
from src.versions import matches, select_version


class RegistryTests(unittest.TestCase):
    """Проверить метаданные без обращения к внешней сети."""

    def test_requested_version_and_cache(self):
        """Используется указанная версия, метаданные читаются один раз."""
        data = {"versions": {
            "1.0.0": {"dependencies": {"child": "^1.0.0"}},
            "2.0.0": {"dependencies": {"other": "2.0.0"}},
        }}
        with patch("src.registry.read_json", return_value=data) as reader:
            repo = Registry("https://example.org")
            self.assertEqual(repo.dependencies("@scope/pkg", "1.0.0"),
                             {"child": "^1.0.0"})
            repo.dependencies("@scope/pkg", "2.0.0")
            reader.assert_called_once_with(
                "https://example.org/%40scope%2Fpkg")
            with self.assertRaises(AppError):
                repo.dependencies("@scope/pkg", "9.0.0")

    def test_network_and_json_errors(self):
        """Сетевые ошибки и повреждённые ответы превращаются в AppError."""
        with patch("src.registry.urlopen", side_effect=OSError("offline")):
            with self.assertRaises(AppError):
                read_json("https://example.org")
        for value in (b"broken", b"[]"):
            response = MagicMock()
            response.__enter__.return_value.read.return_value = value
            with patch("src.registry.urlopen", return_value=response):
                with self.assertRaises(AppError):
                    read_json("https://example.org")

    def test_dependencies_validation(self):
        """Отсутствующие зависимости допустимы, неверные типы запрещены."""
        self.assertEqual(dependencies_of({}), {})
        for value in ([], {"x": 7}, {"x": ""}):
            with self.assertRaises(AppError):
                dependencies_of({"dependencies": value})

    def test_ranges(self):
        """Caret, tilde, OR, маски, сравнения и интервалы работают."""
        examples = [("1.2.3", "^1.0.0", True),
                    ("2.0.0", "^1.0.0", False),
                    ("0.3.0", "^0.2.1", False),
                    ("0.0.4", "^0.0.3", False),
                    ("1.3.0", "~1.2.0", False),
                    ("1.2.5", "1.2.x", True),
                    ("0.9.0", "^0.x", True),
                    ("8.0.0", "^*", True),
                    ("1.9.0", "~1.x", True),
                    ("3.0.0", "1.x || >=3 <4", True),
                    ("2.9.0", "1.0.0 - 2", True),
                    ("1.2.3", ">= 1.0 < 2", True)]
        for version, expression, expected in examples:
            with self.subTest(expression=expression):
                self.assertEqual(matches(version, expression), expected)

    def test_selection_and_unsupported_sources(self):
        """Выбирается максимальная версия; git/file не угадываются."""
        versions = {"1.0.0": {}, "1.9.0": {}, "2.0.0-beta": {}}
        self.assertEqual(select_version(versions, "^1.0.0"), "1.9.0")
        self.assertEqual(select_version(versions, "2.0.0-beta"),
                         "2.0.0-beta")
        with self.assertRaises(AppError):
            select_version(versions, "git+https://example.org/repo")
