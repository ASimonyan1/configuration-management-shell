"""Запуск демонстрационных конфигураций текущего этапа."""

import subprocess
import sys
from pathlib import Path


def main():
    """Выполнить независимые примеры через тот же интерпретатор Python."""
    root = Path(__file__).resolve().parents[1]
    names = ['chain', 'cycle', 'diamond', 'isolated', 'depth', 'filter']
    for name in names:
        command = [sys.executable, "-m", "src.main", "--config",
                   f"examples/{name}.toml"]
        print("Пример:", name, flush=True)
        subprocess.run(command, cwd=root, check=False)


if __name__ == "__main__":
    main()
