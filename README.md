# Вариант 26: этап 4 - основные команды

Отдельная версия для сдачи этапа 4. Язык Python, GUI на Tkinter.
Сохраняется функциональность предыдущих этапов. Каждая ветка содержит
результат своего этапа; следующие этапы в ней отсутствуют.

## Запуск и настройки

Python 3.10+ с Tkinter, графическая среда. Сторонние библиотеки не нужны.
Сборка не требуется. Запускайте из корня проекта:

```powershell
.\run.bat
python -m src.main --config config.json
python -m src.main --vfs vfs.csv --prompt "student> "
python -m unittest discover -s tests -v
```

Linux/macOS: `sh run.sh`. Без аргументов скрипты используют config.json.
Для ручного ввода без сценария: `.\run.bat --vfs vfs.csv`.
В PyCharm: Python с Tkinter; Module name src.main; Working directory -
корень проекта; Parameters `--config config.json`.

CLI: --vfs (CSV), --prompt (приглашение), --script (стартовый сценарий),
--config (JSON). JSON содержит строки или null в полях vfs, prompt, script.
CLI перекрывает JSON, включая пустой prompt. Отсутствующий prompt означает
`$ `. Путь VFS обязателен с третьего этапа. Относительные пути считаются
от рабочего каталога. Ошибки JSON/CSV выводятся в терминал с кодом 2.
Все параметры запуска отображаются в окне.

## VFS

CSV имеет поля path,type,content,encoding,owner. Типы file/dir;
Для каждого файла encoding=base64, включая текстовые и пустые файлы.
После декодирования UTF-8 текст доступен текстовым операциям. Вложенные каталоги представлены POSIX-путями.
Пропущенные родители создаются в памяти. Повторные пути, неверные поля,
повреждённый base64 и конфликты типов отклоняются.
Ошибка загрузки не заменяет ранее загруженную VFS.

Источник читается при запуске, не распаковывается и не изменяется.
Дальнейшие операции работают в памяти. vfs_min.csv содержит один файл;
vfs_nested.csv - несколько файлов и каталог /a/b/c; vfs.csv - текстовые
и двоичные данные, каталог /home/student/docs/project (три уровня).

## Команды

- `ls [-l] [ПУТЬ]`: дети каталога или отдельный файл; -l показывает
  тип, владельца и размер в байтах.
- `cd [ПУТЬ]`: смена каталога VFS, без пути переход в корень.
- `rev ФАЙЛ`: переворачивает символы каждой строки текстового файла.
- `tail [-n N | -N] ФАЙЛ`: последние N строк (по умолчанию 10).
- `who`: имя пользователя ОС, компьютер и текущий каталог VFS.

`exit` без аргументов закрывает окно. Неизвестные команды, неверные флаги,
лишние аргументы и ошибки путей обрабатываются
сообщениями об ошибке. Парсер делит ввод по пробельным символам без обработки
кавычек, перенаправлений и конвейеров. Заголовок - реальные username@hostname.

## Сценарии и демонстрация

Стартовый сценарий UTF-8 содержит одну команду на строку. Пустые строки
и отдельные комментарии Python `# ...` пропускаются. GUI показывает
ввод, результат и ошибку; ошибка команды не останавливает сценарий.
exit прекращает выполнение. После конца сценария доступен ручной ввод.

```powershell
.\examples\check_config.bat
.\examples\check_overrides.bat
.\examples\check_vfs.bat
.\examples\check_commands.bat
```

В Linux/macOS запускайте одноимённые scripts examples/*.sh через sh.
check_config и check_overrides передают все четыре параметра CLI.
check_vfs проверяет три структуры VFS и ошибку отсутствующего CSV.
check_commands запускает сценарии всех режимов команд и ошибочных аргументов.
Если окно не закрывается автоматически, закройте его для следующего запуска.


## Требования этапа 4

1. ls и cd выполняют настоящие операции в VFS.
2. Реализованы команды rev, tail и who.
3. Скрипты и тесты покрывают режимы команд, аргументы, пути и ошибки.
4. Результат этапа сохранён коммитом в формате тип: описание.

## Функции и структура

- src/main.py: build_shell проверяет настройки и загружает CSV; main создаёт
  GUI, показывает параметры, запускает сценарий и цикл событий.
- src/config.py: AppConfig хранит настройки; parse_args читает CLI;
  load_json_config читает JSON; merge_config применяет приоритет;
  resolve_config собирает настройки; iter_script_commands читает сценарий.
- src/gui.py: __init__, _create_output, _create_input создают интерфейс;
  append пишет журнал; run_command и _on_enter обрабатывают ввод;
  show_config выводит настройки; start_script и _script_step исполняют
  сценарий через очередь Tkinter.after.
- src/shell.py: ShellEmulator хранит состояние; window_title читает данные
  ОС; execute разбирает команду; _cmd_ls, _cmd_cd и _cmd_exit обрабатывают
  операции. require_count и parse_ls проверяют аргументы; format_node
  форматирует ls; parse_count и parse_tail разбирают tail; _cmd_rev,
  _cmd_tail и _cmd_who реализуют текстовые команды и сведения о сеансе.
- src/vfs.py: VFSNode представляет узел; normalize разрешает POSIX-путь;
  decode_content декодирует данные; validate_node_fields и parse_node
  проверяют CSV. VirtualFileSystem.__init__, resolve, load_csv, _read_rows,
  _add_node загружают дерево; exists, get, list_dir, change_dir, read_text
  работают в памяти.
- src/errors.py: EmulatorError представляет пользовательскую ошибку.
- tests/: проверки настроек, VFS, команд и GUI.
  GUI-тесты подменяют виджеты; демонстрация окна выполняется вручную.
- examples/: скрипты реальной ОС; scripts/: сценарии эмулятора.
- tools/check_style.py: check_file, check_functions и main проверяют
  структуру, длину строк и функций, аргументы и docstring.
- .github/workflows/checks.yml: автоматические проверки в GitHub Actions.

Все функции имеют docstring. src, tests, README.md, .gitignore,
run.bat/run.sh присутствуют; настройки IDE и кэш Python исключены из Git.
Коммиты имеют формат `тип: описание`, без области в скобках.

## Ветки для сдачи

Один репозиторий, отдельная версия для каждого этапа:

- [submission-1: REPL](https://github.com/ASimonyan1/configuration-management-shell/tree/submission-1)
- [submission-2: конфигурация](https://github.com/ASimonyan1/configuration-management-shell/tree/submission-2)
- [submission-3: VFS](https://github.com/ASimonyan1/configuration-management-shell/tree/submission-3)
- [submission-4: основные команды](https://github.com/ASimonyan1/configuration-management-shell/tree/submission-4)
- [submission-5: chown](https://github.com/ASimonyan1/configuration-management-shell/tree/submission-5)

На GitHub нажмите название текущей ветки над списком файлов и выберите
нужную submission-N. Для скачивания этой версии: Code → Download ZIP.
В локальном Git-проекте: `git switch submission-N`.


## Исправление формата VFS

Содержимое всех файлов в vfs*.csv хранится в Base64. Поле content
декодируется с проверкой корректности; обычный текст без Base64
отклоняется. UTF-8 текст и двоичные данные различаются после
декодирования. Пустой файл представлен пустой строкой Base64.
