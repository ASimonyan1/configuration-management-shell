#!/bin/sh
cd -- "$(dirname -- "$0")/.." || exit 1
sh run.sh --vfs vfs_min.csv --script scripts/vfs_min.txt
sh run.sh --vfs vfs_nested.csv --script scripts/vfs_nested.txt
sh run.sh --vfs vfs.csv --script scripts/stage3.txt
sh run.sh --vfs missing.csv
