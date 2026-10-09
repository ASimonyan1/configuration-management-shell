#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --vfs data/override.csv --prompt "" --script scripts/exit.txt --config config.json
