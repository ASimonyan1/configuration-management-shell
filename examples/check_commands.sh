#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --config config.json --vfs vfs.csv --prompt "commands> " --script scripts/stage4.txt
