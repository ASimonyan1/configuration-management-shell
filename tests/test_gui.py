"""Проверки диалога и сценариев без зависимости от оконной системы."""

from unittest.mock import Mock, patch

from src.config import AppConfig
from src.gui import EmulatorGUI
from src.main import build_shell, main
from src.shell import ShellEmulator
from src.vfs import VirtualFileSystem
from tests.support import CSV, TempCase


class GUITests(TempCase):
    """Использовать настоящую оболочку и подменить только виджеты GUI."""

    def setUp(self):
        """Подготовить оболочку, журнал и очередь событий окна."""
        super().setUp()
        vfs = VirtualFileSystem()
        vfs.load_csv(self.write_file(CSV))
        self.gui = EmulatorGUI.__new__(EmulatorGUI)
        self.gui.root = Mock()
        self.gui.shell = ShellEmulator(vfs, "emu> ")
        self.gui.append = Mock()

    def transcript(self):
        """Объединить все добавленные в журнал фрагменты."""
        return "".join(call.args[0] for call in self.gui.append.call_args_list)

    def test_script_displays_input_output_errors_and_stops_at_exit(self):
        """Сценарий продолжает работу после ошибки и останавливается на exit."""
        path = self.write_file("# note\nls\nunknown\nexit\nls /missing\n")
        self.gui.start_script(path)
        while self.gui.root.after.call_args_list:
            call = self.gui.root.after.call_args_list.pop(0)
            call.args[1]()
        text = self.transcript()
        self.assertIn("emu> ls\n", text)
        self.assertIn("home/", text)
        self.assertIn("Ошибка: unknown", text)
        self.assertNotIn("ls /missing", text)
        self.gui.root.destroy.assert_called_once()

    def test_config_is_visible_and_bad_script_is_reported(self):
        """Журнал показывает все настройки и ошибки загрузки сценария."""
        self.gui.show_config(AppConfig("v.csv", "emu> ", "s.txt"), "c.json")
        self.gui.start_script(self.folder / "missing")
        for value in ("v.csv", "emu> ", "s.txt", "c.json", "Ошибка:"):
            self.assertIn(value, self.transcript())

    def test_enter_clears_input_and_runs_command(self):
        """Enter отправляет команду и очищает поле ввода."""
        self.gui.entry = Mock()
        self.gui.entry.get.return_value = "ls"
        self.gui._on_enter()
        self.gui.entry.delete.assert_called_once_with(0, "end")
        self.assertIn("home/", self.transcript())

    def test_window_initialization(self):
        """Окно получает заголовок ОС, журнал и поле с обработчиком Enter."""
        with patch("src.gui.tk.Text"), patch("src.gui.ttk.Frame"):
            with patch("src.gui.ttk.Label"), patch("src.gui.ttk.Entry"):
                gui = EmulatorGUI(self.gui.root, self.gui.shell)
        self.gui.root.title.assert_called_once_with(self.gui.shell.window_title)
        gui.entry.bind.assert_called_once_with("<Return>", gui._on_enter)
        gui.output.insert.assert_called_once()

    def test_bad_startup_returns_error_before_opening_window(self):
        """Некорректная конфигурация не открывает GUI."""
        with patch("src.main.tk.Tk") as window, patch("sys.stderr"):
            self.assertEqual(main([]), 2)
            self.assertEqual(main(["--vfs", "missing.csv"]), 2)
        window.assert_not_called()

    def test_build_shell_uses_cli_prompt(self):
        """Итоговый prompt сохраняет явно переданную пустую строку."""
        args = Mock(config=None, vfs=str(self.write_file(CSV)), prompt="")
        args.script = None
        shell, config = build_shell(args)
        self.assertEqual(shell.prompt, "")
        self.assertEqual(config.vfs, args.vfs)
