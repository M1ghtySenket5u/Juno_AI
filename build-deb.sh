#!/usr/bin/env bash
# Build a simple .deb that installs Juno AI under /opt/juno-ai (run from this folder: ./build-deb.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VER="${JUNO_DEB_VERSION:-1.0.0}"
STAGE="$(mktemp -d)"
PKG="$STAGE/juno-ai_${VER}_all"
mkdir -p "$PKG/DEBIAN" "$PKG/opt/juno-ai"

cat >"$PKG/DEBIAN/control" <<EOF
Package: juno-ai
Version: $VER
Section: utils
Priority: optional
Architecture: all
Maintainer: Juno AI User <local@localhost>
Depends: python3 (>= 3.10), python3-venv, python3-pip
Description: Juno AI — Linux Mint desktop buddy (offline-first)
 Desktop chat assistant themed for Linux Mint learners; optional OpenAI or local HTTP API. Uses a local venv under /opt/juno-ai.
EOF

cat >"$PKG/DEBIAN/postinst" <<'EOS'
#!/bin/sh
set -e
cd /opt/juno-ai
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r /opt/juno-ai/requirements.txt
chmod +x /opt/juno-ai/juno-ai.sh || true
update-desktop-database /usr/share/applications 2>/dev/null || true
EOS
chmod 755 "$PKG/DEBIAN/postinst"

cp -a "$ROOT/main.py" "$ROOT/config_store.py" "$ROOT/juno_system_prompt.py" \
  "$ROOT/juno_offline.py" "$ROOT/mint_fun_facts.py" "$ROOT/galaxy_widget.py" \
  "$ROOT/requirements.txt" "$ROOT/juno-ai.sh" "$ROOT/juno-ai.desktop.template" \
  "$ROOT/install-linux.sh" "$ROOT/build-deb.sh" "$ROOT/README.md" "$ROOT/INSTALL.md" \
  "$PKG/opt/juno-ai/"
chmod +x "$PKG/opt/juno-ai/juno-ai.sh" "$PKG/opt/juno-ai/install-linux.sh" "$PKG/opt/juno-ai/build-deb.sh"

mkdir -p "$PKG/usr/share/applications"
sed "s|__INSTALL_DIR__|/opt/juno-ai|g" "$PKG/opt/juno-ai/juno-ai.desktop.template" \
  >"$PKG/usr/share/applications/juno-ai.desktop"

mkdir -p "$PKG/usr/bin"
ln -sf /opt/juno-ai/juno-ai.sh "$PKG/usr/bin/juno-ai"

dpkg-deb --root-owner-group --build "$PKG" "$ROOT/juno-ai_${VER}_all.deb"
rm -rf "$STAGE"
echo "Built: $ROOT/juno-ai_${VER}_all.deb"
