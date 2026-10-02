#!/bin/sh
cd -- "$(dirname -- "$0")" || exit 1
if [ "$#" -eq 0 ]; then
    set -- --config config.json
fi
exec python3 -m src.main "$@"
