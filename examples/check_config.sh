#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --config config.json --vfs vfs.csv --prompt "cli> " --script scripts/stage2.txt
