#!/usr/bin/env bash
# Launch Juno AI from this directory (prefers .venv when present).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
VENV_PY="$DIR/.venv/bin/python"

if [[ -x "$VENV_PY" ]]; then
  exec "$VENV_PY" "$DIR/main.py" "$@"
fi

echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ Juno AI: virtual environment not found at                      │"
echo "│   $DIR/.venv"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""
echo "Install Juno first. Copy this entire block into Terminal, then press Enter:"
echo ""
echo "  cd \"$DIR\" && chmod +x install-linux.sh juno-ai.sh && ./install-linux.sh"
echo ""

if command -v python3 >/dev/null 2>&1; then
  if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Optional — if you prefer system packages instead of .venv, on Mint try:"
    echo ""
    echo "  sudo apt update && sudo apt install -y python3-pyqt6 python3-pip"
    echo "  cd \"$DIR\" && python3 -m pip install --user -r requirements.txt"
    echo ""
  fi
fi

echo "Trying system Python3 anyway (may fail if PyQt6 / openai are missing)…"
exec python3 "$DIR/main.py" "$@"
