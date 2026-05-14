#!/usr/bin/env bash
# Juno AI — installer for Linux Mint and Debian/Ubuntu-based systems.
# Run from the juno-ai folder:   chmod +x install-linux.sh && ./install-linux.sh
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================="
echo "  Juno AI — step-by-step installer"
echo "  Project folder: $DIR"
echo "=========================================="

step() {
  echo ""
  echo "==> Step $1: $2"
}

step 1 "Verify python3 is installed"
if ! command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "MISSING: python3 was not found in your PATH."
  echo "Copy these lines into Terminal (one block), press Enter, then run this installer again:"
  echo ""
  echo "  sudo apt update"
  echo "  sudo apt install -y python3 python3-venv python3-pip"
  echo ""
  exit 1
fi
python3 --version

step 2 "Verify Python 3.10 or newer"
if ! python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"; then
  echo ""
  echo "Juno needs Python 3.10 or newer. Your interpreter reports:"
  python3 --version
  echo "Upgrade your system Python or use a newer Linux Mint, then retry."
  exit 1
fi

step 3 "Verify the venv module (package python3-venv)"
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo ""
  echo "MISSING: 'python3 -m venv' does not work (python3-venv is usually absent)."
  echo "Copy into Terminal, then re-run this installer:"
  echo ""
  echo "  sudo apt update"
  echo "  sudo apt install -y python3-venv python3-pip"
  echo ""
  exit 1
fi

chmod +x "$DIR/juno-ai.sh" "$DIR/build-deb.sh" 2>/dev/null || true

step 4 "Create or reuse virtual environment in .venv"
if [[ -d "$DIR/.venv" ]]; then
  echo "    Note: .venv already exists — it will be reused."
  echo "    For a completely clean reinstall:  rm -rf \"$DIR/.venv\""
fi
python3 -m venv "$DIR/.venv"

step 5 "Install Python packages with pip (inside .venv)"
# shellcheck disable=SC1091
source "$DIR/.venv/bin/activate"
python3 -m pip install --upgrade pip
python3 -m pip install -r "$DIR/requirements.txt"

step 6 "Install the Cinnamon / desktop menu shortcut"
DESKTOP_USER="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$DESKTOP_USER"
DESKTOP_OUT="$DESKTOP_USER/juno-ai.desktop"
sed "s|__INSTALL_DIR__|$DIR|g" "$DIR/juno-ai.desktop.template" >"$DESKTOP_OUT"
chmod 644 "$DESKTOP_OUT"
echo "    Wrote: $DESKTOP_OUT"

echo ""
echo "=========================================="
echo "  Installation finished."
echo ""
echo "  Next — start Juno (pick one):"
echo "    • Menu: Super key → type \"Juno AI\" → Enter"
echo "    • Terminal (copy as one line):"
echo "        cd \"$DIR\" && ./juno-ai.sh"
echo ""
echo "  The first launch opens a short setup guide with copy-paste"
echo "  commands if anything is still missing."
echo "=========================================="

if command -v update-desktop-database >/dev/null 2>&1; then
  echo ""
  echo "==> Updating desktop database (optional)…"
  update-desktop-database "$DESKTOP_USER" 2>/dev/null || true
fi
