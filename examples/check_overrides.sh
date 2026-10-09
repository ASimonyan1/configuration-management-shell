#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --config config.json --vfs vfs_min.csv --prompt "min> " --script scripts/vfs_min.txt
sh run.sh --config config.json --vfs vfs_nested.csv --prompt "deep> " --script scripts/vfs_nested.txt
sh run.sh --config config.json --vfs vfs.csv --prompt "full> " --script scripts/stage3.txt
