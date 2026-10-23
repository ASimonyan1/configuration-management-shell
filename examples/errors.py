"""Демонстрация ошибок каждого параметра TOML."""

import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    """Показать ошибки шести параметров и синтаксиса TOML."""
    root = Path(__file__).resolve().parents[1]
    valid = (root / "examples/is-odd.toml").read_text(encoding="utf-8")
    replacements = [
        ('"is-odd"', '"bad name"'),
        ('"https://registry.npmjs.org"', '"invalid"'),
        ('test_mode = false', 'test_mode = "yes"'),
        ('"3.0.1"', '"not-a-version"'),
        ('max_depth = 8', 'max_depth = -1'),
        ('filter_substring = ""', 'filter_substring = 123'),
    ]
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "invalid.toml"
        for old, new in replacements:
            path.write_text(valid.replace(old, new), encoding="utf-8")
            print("Неверное значение:", new, flush=True)
            result = subprocess.run(
                [sys.executable, "-m", "src.main", "--config", str(path)],
                cwd=root, check=False)
            if result.returncode != 2:
                raise RuntimeError("Ожидался код ошибки 2")


if __name__ == "__main__":
    main()
