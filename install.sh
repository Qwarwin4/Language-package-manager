#!/bin/bash
set -e

# ─────────────────────────────────────────────
#  LPM — Universal Package Manager Wrapper
#  install.sh
# ─────────────────────────────────────────────

INSTALL_DIR="/opt/lpm"
BIN_LINK="/usr/local/bin/lpm"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[ℹ]  $*${NC}"; }
success() { echo -e "${GREEN}[✔]  $*${NC}"; }
warn()    { echo -e "${YELLOW}[⚠]  $*${NC}"; }
error()   { echo -e "${RED}[✘]  $*${NC}"; }
section() { echo -e "\n${BOLD}━━━  $*  ━━━${NC}"; }

LPM_VERSION=$(python3 -c "import re; print(re.search(r'VERSION = \"(.+?)\"', open('$(dirname "$0")/main.py').read()).group(1))")

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  LPM Installer  v${LPM_VERSION}${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ── 1. Python (required) ──────────────────────────────────────────────────────
section "Python"

if ! command -v python3 &>/dev/null; then
    error "Python3 is required but not installed. Please install it and re-run."
    exit 1
fi

info "Installing Python dependency: distro"
pip3 install distro --break-system-packages 2>/dev/null || pip3 install distro
success "Python ready ($(python3 --version))"

# ── 2. Install LPM ────────────────────────────────────────────────────────────
section "Installing LPM"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info "Creating $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"

info "Copying files..."
sudo cp "$SCRIPT_DIR/main.py"         "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/pypi_handler.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/utils.py"        "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/updater.py"      "$INSTALL_DIR/"
# packages.json lives in ~/.lpm/ (created automatically on first run)

info "Creating wrapper command..."
sudo tee "$INSTALL_DIR/lpm_cmd" > /dev/null << 'CMDEOF'
#!/bin/bash
cd /opt/lpm
exec python3 main.py "$@"
CMDEOF
sudo chmod +x "$INSTALL_DIR/lpm_cmd"

if [ -L "$BIN_LINK" ] || [ -f "$BIN_LINK" ]; then
    sudo rm -f "$BIN_LINK"
fi
sudo ln -s "$INSTALL_DIR/lpm_cmd" "$BIN_LINK"
success "Symlink created: $BIN_LINK"

echo ""
echo -e "${BOLD}${GREEN}✅  LPM installation complete!${NC}"
echo "────────────────────────────────────────────────────"
echo -e "  ${CYAN}lpm install <pkg> --python${NC}       → pip"
echo -e "  ${CYAN}lpm install <pkg> --cpp${NC}          → apt/pacman/dnf"
echo -e "  ${CYAN}lpm install <pkg> --local${NC}        → install into current project"
echo -e "  ${CYAN}lpm remove  <pkg> [--flag]${NC}       → remove"
echo -e "  ${CYAN}lpm list${NC}                         → show registry"
echo -e "  ${CYAN}lpm updates${NC}                      → check for new version"
echo "────────────────────────────────────────────────────"
