#!/usr/bin/env bash
# Juno AI — install helper for Linux Mint (and most Debian/Ubuntu-based systems).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "==> Juno AI installer"
echo "    Directory: $DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install with: sudo apt install python3 python3-venv python3-pip"
  exit 1
fi

chmod +x "$DIR/juno-ai.sh" "$DIR/build-deb.sh" 2>/dev/null || true

echo "==> Creating virtual environment in .venv"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

DESKTOP_USER="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$DESKTOP_USER"
DESKTOP_OUT="$DESKTOP_USER/juno-ai.desktop"
echo "==> Writing menu shortcut to $DESKTOP_OUT"
sed "s|__INSTALL_DIR__|$DIR|g" "$DIR/juno-ai.desktop.template" >"$DESKTOP_OUT"
chmod +644 "$DESKTOP_OUT"

echo ""
echo "Installation finished."
echo "  • Start from the menu: look for \"Juno AI\""
echo "  • Or run: $DIR/juno-ai.sh"
echo "  • First launch: works fully offline. File → Settings only if you add OpenAI or a local HTTP API."
echo ""
echo "Updating desktop database (optional)…"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_USER" 2>/dev/null || true
fi
