# Вариант №26: этап 1 — REPL

Восстановленный минимальный прототип GUI на Python 3.10+ с Tkinter.
Запуск из корня: `python -m src.main`, `.\run.bat` или `sh run.sh`.
Сборка и сторонние пакеты не нужны. Тестов на этом этапе ещё нет;
папка `tests` сохранена файлом `.gitkeep`.

`ShellEmulator.execute` делит строку по пробелам. `ls` и `cd` — заглушки,
выводящие имя и аргументы, `exit` закрывает окно. Заголовок использует
реальные данные ОС. `EmulatorGUI` показывает ввод, вывод и ошибки.
`_check_args` проверяет аргументы. Методы GUI создают журнал и поле ввода,
обрабатывают Enter и закрытие. Все функции имеют docstring.
Настройки запуска появятся на втором этапе.


## Этап 2 — конфигурация

Добавлены `--vfs`, `--prompt`, `--script`, `--config` и JSON-поля
`vfs`, `prompt`, `script`. CLI перекрывает JSON. Пути относительны корню.
VFS ещё не читается. `resolve_config` объединяет настройки,
`load_json_config` проверяет JSON, `iter_script_commands` читает сценарий.
GUI выводит настройки, команды и результаты; комментарии `#` пропускаются.
Функции и остальные методы описаны в docstring.

Запуск: `python -m src.main --config config.json` или `.\run.bat`.
Проверки: `python -m unittest discover -s tests -v`.
Демонстрация: `examples/check_config.bat`, `examples/check_overrides.bat`.

## Этап 3 — VFS

Подключена CSV-система в памяти с полями path,type,content,encoding,owner.
Файлы text/base64, каталоги dir, вложенность не ограничена.
`VirtualFileSystem.load_csv` загружает и проверяет CSV; `resolve`, `get`,
`list_dir`, `change_dir`, `read_text` работают в памяти. Функции разбора
и проверки строк CSV отделены от дерева. Детали описаны в docstring.
Работают `ls [-l] [ПУТЬ]`, `cd [ПУТЬ]`, `exit`.

Пример: `ls /`, `cd /home/student/docs/project`, `ls -l`, `cd /missing`.
`examples/check_vfs.bat` и `examples/check_overrides.bat` демонстрируют
минимальную, многофайловую и вложенную VFS. `scripts/stage3.txt` проверяет
режимы команд и ошибки. Тесты: `python -m unittest discover -s tests -v`.
