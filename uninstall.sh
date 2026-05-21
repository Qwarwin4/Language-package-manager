#!/bin/bash
set -e

# ─────────────────────────────────────────────
#  LPM — Universal Package Manager Wrapper
#  uninstall.sh  v1.2.0
# ─────────────────────────────────────────────

INSTALL_DIR="/opt/lpm"
BIN_LINK="/usr/local/bin/lpm"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[ℹ]  $*${NC}"; }
success() { echo -e "${GREEN}[✔]  $*${NC}"; }
warn()    { echo -e "${YELLOW}[⚠]  $*${NC}"; }
section() { echo -e "\n${BOLD}━━━  $*  ━━━${NC}"; }

LPM_VERSION=$(python3 -c "import re; print(re.search(r'VERSION = \"(.+?)\"', open('$(dirname "$0")/main.py').read()).group(1))")

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  LPM Uninstaller  v${LPM_VERSION}${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "This will remove LPM from your system."
echo ""
read -r -p "Continue? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    info "Aborted."
    exit 0
fi

# ── 1. Remove symlink ─────────────────────────────────────────────────────────
section "Removing lpm command"

if [ -L "$BIN_LINK" ] || [ -f "$BIN_LINK" ]; then
    sudo rm -f "$BIN_LINK"
    success "Removed $BIN_LINK"
else
    warn "$BIN_LINK not found, skipping."
fi

# ── 2. Remove install directory ───────────────────────────────────────────────
section "Removing $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    sudo rm -rf "$INSTALL_DIR"
    success "Removed $INSTALL_DIR"
else
    warn "$INSTALL_DIR not found, skipping."
fi

# ── Remove user data directory ────────────────────────────────────────────────
section "Removing user data (~/.lpm)"

LPM_USER_DIR="$HOME/.lpm"
if [ -d "$LPM_USER_DIR" ]; then
    read -r -p "Remove ~/.lpm (package registry)? (y/n): " RM_DATA
    if [[ "$RM_DATA" == "y" || "$RM_DATA" == "Y" ]]; then
        rm -rf "$LPM_USER_DIR"
        success "Removed $LPM_USER_DIR"
    else
        info "Keeping $LPM_USER_DIR"
    fi
else
    info "~/.lpm not found, skipping."
fi

# ── 3. Remove Python dependency ───────────────────────────────────────────────
section "Python dependency"

info "Removing 'distro' package that was installed by LPM..."
pip3 uninstall -y distro 2>/dev/null \
    || pip3 uninstall -y distro --break-system-packages 2>/dev/null \
    || warn "Could not remove 'distro' automatically. Remove manually: pip uninstall distro"
success "'distro' removed."

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}✅  LPM has been removed.${NC}"
info "Rust, Node.js and Dart were NOT touched — they are independent tools."
info "Local project files (.venv, node_modules, Cargo.toml, conanfile.txt) were NOT touched."
info "If you kept ~/.lpm, your package registry is still there."
