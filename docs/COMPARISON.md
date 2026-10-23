# Сравнение с npm ls

Дата: 23.10.2026. npm 11.6.2, Graphviz 16.1.0.

Анализатор получает данные сам через urllib. npm запускается
только отдельно для требуемого заданием сравнения.

Команды проверки для каждого PACKAGE@VERSION:

```sh
npm install PACKAGE@VERSION --package-lock-only --ignore-scripts --no-audit --no-fund
npm ls --all --package-lock-only --json
npm ls --all --package-lock-only
```

Установка выполняется в отдельном временном каталоге;
lifecycle-скрипты отключены, node_modules не создаётся.

| Пакет | Узлы | Рёбра | Совпадение с npm ls |
| --- | ---: | ---: | --- |
| is-odd@3.0.1 | 2 | 1 | Да |
| is-even@1.0.0 | 5 | 4 | Да |
| kind-of@6.0.3 | 1 | 0 | Да |

Для трёх выбранных пакетов расхождений узлов/рёбер нет.
Служебный корень verification из npm ls не относится к пакету
и исключается при сравнении. npm рисует дерево с повторными
узлами, анализатор объединяет одинаковые пары имя/версия.
Для иных пакетов возможны различия: npm учитывает peer/optional,
lock-файл и дедупликацию, здесь анализируется dependencies.
Фильтр и глубина также могут намеренно усекать граф.

Примеры изображений создаются командой `python examples/demo.py`.
Исходники DOT и фактический вывод npm ls находятся рядом.
SVG сохраняются локально в output/ и не коммитятся как артефакты.

[Документация npm ls](https://docs.npmjs.com/cli/v11/commands/npm-ls/)
[Graphviz CLI](https://graphviz.org/doc/info/command.html)
