#!/usr/bin/env bash
# Launch Juno AI from this directory (uses local .venv if present).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
if [[ -x "$DIR/.venv/bin/python" ]]; then
  exec "$DIR/.venv/bin/python" "$DIR/main.py" "$@"
fi
exec python3 "$DIR/main.py" "$@"
