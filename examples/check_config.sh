#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --vfs data/cli.csv --prompt "cli> " --script scripts/stage2.txt --config config.json
