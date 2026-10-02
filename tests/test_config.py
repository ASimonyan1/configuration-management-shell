"""Проверки JSON, CLI и стартовых сценариев."""

from src.config import (
    AppConfig,
    iter_script_commands,
    load_json_config,
    merge_config,
    parse_args,
    resolve_config,
)
from src.errors import EmulatorError
from tests.support import TempCase


class ConfigTests(TempCase):
    """Проверить приоритеты, необязательные поля и ошибки чтения."""

    def test_cli_overrides_all_json_values(self):
        """Каждый переданный параметр CLI перекрывает JSON."""
        path = self.write_file(
            '{"vfs":"old.csv","prompt":"old>","script":"old.txt"}'
        )
        args = parse_args([
            "--config", str(path), "--vfs", "new.csv",
            "--prompt", "", "--script", "new.txt",
        ])
        self.assertEqual(
            resolve_config(args), AppConfig("new.csv", "", "new.txt")
        )

    def test_missing_cli_values_preserve_json(self):
        """Отсутствие аргументов не стирает настройки файла."""
        config = AppConfig("v.csv", "emu> ", "commands.txt")
        self.assertEqual(merge_config(config, None, None, None), config)

    def test_empty_config_and_defaults(self):
        """Пустой объект и запуск без настроек дают значения None."""
        self.assertEqual(load_json_config(self.write_file("{}")), AppConfig())
        self.assertEqual(resolve_config(parse_args([])), AppConfig())

    def test_bad_json_and_types(self):
        """Неверный JSON и некорректные типы дают понятную ошибку."""
        for text in ("{", "[]", '{"vfs":42}', '{"prompt":false}'):
            with self.subTest(text=text), self.assertRaises(EmulatorError):
                load_json_config(self.write_file(text))

    def test_missing_config(self):
        """Отсутствующий файл не вызывает необработанный OSError."""
        with self.assertRaises(EmulatorError):
            load_json_config(self.folder / "missing.json")

    def test_script_comments_and_blank_lines(self):
        """Сценарий пропускает пустые строки и отдельные комментарии."""
        path = self.write_file("# title\n\n  # note\nls\n cd /home\n")
        self.assertEqual(list(iter_script_commands(path)), ["ls", " cd /home"])

    def test_missing_and_non_utf8_scripts(self):
        """Ошибки открытия и декодирования сценария оборачиваются."""
        path = self.folder / "bad.txt"
        with self.assertRaises(EmulatorError):
            list(iter_script_commands(path))
        path.write_bytes(b"\xff")
        with self.assertRaises(EmulatorError):
            list(iter_script_commands(path))
