"""Запуск демонстрационных конфигураций текущего этапа."""

import subprocess
import sys
from pathlib import Path


def main():
    """Выполнить независимые примеры через тот же интерпретатор Python."""
    root = Path(__file__).resolve().parents[1]
    names = ['is-odd', 'is-even', 'kind-of']
    for name in names:
        command = [sys.executable, "-m", "src.main", "--config",
                   f"examples/{name}.toml"]
        command += ["--output", f"output/{name}"]
        print("Пример:", name, flush=True)
        subprocess.run(command, cwd=root, check=False)


if __name__ == "__main__":
    main()
