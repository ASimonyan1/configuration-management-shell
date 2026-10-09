"""Проверки запуска и исполнения сценария без графического дисплея."""

from unittest.mock import Mock, patch

from src.config import AppConfig, parse_args
from src.gui import EmulatorGUI
from src.main import build_shell, main
from src.shell import ShellEmulator
from tests.support import TempCase


class Stage2Tests(TempCase):
    """Проверить вывод настроек, сценарии и ошибки запуска."""

    def make_gui(self):
        """Создать обработчик GUI с заменёнными виджетами."""
        gui = object.__new__(EmulatorGUI)
        gui.root = Mock()
        gui.shell = ShellEmulator()
        gui.append = Mock()
        return gui

    def drain_script(self, gui):
        """Исполнить отложенные шаги по порядку как цикл Tkinter."""
        while gui.root.after.call_args_list:
            call = gui.root.after.call_args_list.pop(0)
            call.args[1]()

    def test_vfs_path_is_not_opened_and_prompt_is_applied(self):
        """Путь VFS только отображается до третьего этапа."""
        shell, config = build_shell(parse_args([
            "--vfs", "missing.csv", "--prompt", "custom> "
        ]))
        self.assertEqual(shell.prompt, "custom> ")
        self.assertEqual(config.vfs, "missing.csv")
        self.assertEqual(shell.execute("cd /x"),
                         "Команда: cd\nАргументы: ['/x']")

    def test_default_prompt(self):
        """Отсутствие параметров сохраняет приглашение первого этапа."""
        shell, config = build_shell(parse_args([]))
        self.assertEqual(shell.prompt, "$ ")
        self.assertIsNone(config.vfs)

    def test_all_effective_parameters_are_displayed(self):
        """Показать VFS, приглашение, сценарий и путь конфигурации."""
        gui = self.make_gui()
        gui.show_config(AppConfig("v.csv", "$ ", "s.txt"), "c.json")
        output = gui.append.call_args.args[0]
        for value in ("v.csv", "'$ '", "s.txt", "c.json"):
            self.assertIn(value, output)

    def test_script_echoes_input_output_and_continues_after_error(self):
        """Комментарии пропускаются, ошибки не прерывают сценарий."""
        path = self.write_file("# note\n\nls\nunknown\ncd /x\n")
        gui = self.make_gui()
        gui.start_script(path)
        self.drain_script(gui)
        output = "".join(c.args[0] for c in gui.append.call_args_list)
        self.assertNotIn("# note", output)
        self.assertIn("$ ls\nКоманда: ls", output)
        self.assertIn("Ошибка: unknown: неизвестная команда", output)
        self.assertIn("$ cd /x\nКоманда: cd", output)

    def test_exit_stops_script_and_closes_window(self):
        """После exit остальные команды не выполняются."""
        path = self.write_file("exit extra\nls\nexit\nunknown\n")
        gui = self.make_gui()
        gui.start_script(path)
        self.drain_script(gui)
        output = "".join(c.args[0] for c in gui.append.call_args_list)
        self.assertIn("exit: команда не принимает аргументы", output)
        self.assertIn("Команда: ls", output)
        self.assertNotIn("unknown", output)
        gui.root.destroy.assert_called_once()

    def test_missing_script_reports_error_and_keeps_repl(self):
        """Ошибка сценария оставляет интерактивный ввод доступным."""
        gui = self.make_gui()
        gui.start_script(self.folder / "missing.txt")
        gui.root.after.assert_not_called()
        self.assertIn("Ошибка:", gui.append.call_args.args[0])
        gui.run_command("ls")
        self.assertIn("Команда: ls", gui.append.call_args.args[0])

    def test_bad_config_prevents_window_creation(self):
        """Ошибка чтения JSON выводится до открытия окна."""
        with patch("src.main.tk.Tk") as tk_root:
            with patch("src.main.sys.stderr") as error:
                code = main(["--config", str(self.folder / "missing")])
        self.assertEqual(code, 2)
        tk_root.assert_not_called()
        self.assertTrue(error.write.called)
