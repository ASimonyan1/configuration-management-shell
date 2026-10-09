"""Проверка длины строк, функций, docstring и структуры проекта."""

import ast
from pathlib import Path

MAX_PY_LINE = 80
MAX_OTHER_LINE = 120
MAX_FUNCTION_LINES = 40
MAX_ARGUMENTS = 7
MAX_FILE_LINES = 1000
ROOT = Path(__file__).resolve().parents[1]


def check_file(path):
    """Проверить ограничения учебного задания в текстовом файле."""
    lines = path.read_text(encoding="utf-8").splitlines()
    limit = MAX_PY_LINE if path.suffix == ".py" else MAX_OTHER_LINE
    assert len(lines) <= MAX_FILE_LINES, str(path)
    for number, line in enumerate(lines, 1):
        assert len(line) <= limit, (str(path), number, len(line))
    if path.suffix == ".py":
        check_functions(ast.parse("\n".join(lines)), path)


def check_functions(tree, path):
    """Проверить размер, число аргументов и документацию функций."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            size = node.end_lineno - node.lineno + 1
            assert size <= MAX_FUNCTION_LINES, (str(path), node.name, size)
            assert len(node.args.args) <= MAX_ARGUMENTS, node.name
            assert ast.get_docstring(node), (str(path), node.name)


def main():
    """Проверить обязательные пути и исходные текстовые файлы."""
    for name in ("src", "tests", "README.md", ".gitignore", "run.bat"):
        assert (ROOT / name).exists(), name
    for folder in ("src", "tests", "tools", "scripts", "examples", ".github"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                check_file(path)
    for name in ("README.md", "run.bat", "run.sh", "config.json"):
        check_file(ROOT / name)
    print("Оформление проекта проверено.")


if __name__ == "__main__":
    main()
