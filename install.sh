#!/bin/bash
set -e

# ─────────────────────────────────────────────
#  LPM — Universal Package Manager Wrapper
#  install.sh  v1.2.0
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

ask() {
    # ask "Question?" → returns 0 (yes) or 1 (no)
    local ans
    read -r -p "$1 (y/n): " ans
    [[ "$ans" == "y" || "$ans" == "Y" ]]
}

# ── Detect system package manager ────────────────────────────────────────────
detect_manager() {
    if   command -v apt    &>/dev/null; then echo "apt"
    elif command -v pacman &>/dev/null; then echo "pacman"
    elif command -v dnf    &>/dev/null; then echo "dnf"
    else echo "unknown"; fi
}

SYS_MGR=$(detect_manager)

sys_install() {
    case "$SYS_MGR" in
        apt)    sudo apt-get install -y "$@" ;;
        pacman) sudo pacman -S --noconfirm "$@" ;;
        dnf)    sudo dnf install -y "$@" ;;
        *)      error "Unsupported package manager. Install manually: $*"; return 1 ;;
    esac
}

# ── 1. Python (required — LPM itself is Python) ───────────────────────────────
section "Python"

if ! command -v python3 &>/dev/null; then
    error "Python3 is required but not installed. Please install it and re-run."
    exit 1
fi

info "Installing Python dependency: distro"
pip3 install distro --break-system-packages 2>/dev/null || pip3 install distro
success "Python ready ($(python3 --version))"

# ── 2. Rust (optional) ────────────────────────────────────────────────────────
section "Rust"

if command -v cargo &>/dev/null; then
    success "Rust already installed ($(rustc --version))"
else
    warn "Rust (cargo) is not installed."
    if ask "Install Rust via rustup?"; then
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
        # shellcheck disable=SC1091
        source "$HOME/.cargo/env" 2>/dev/null || true
        if command -v cargo &>/dev/null; then
            success "Rust installed ($(rustc --version))"
            for RC in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
                if [ -f "$RC" ] && ! grep -q 'cargo/env' "$RC"; then
                    printf '\n# Rust / Cargo\n. "$HOME/.cargo/env"\n' >> "$RC"
                fi
            done
            info "Cargo env added to shell profiles. Re-open terminal or: source ~/.cargo/env"
        else
            error "Rust installation failed. Install manually: https://rustup.rs"
        fi
    else
        info "Skipping Rust. You can install it later: https://rustup.rs"
        info "  lpm install <pkg> --rust  will remind you if cargo is missing."
    fi
fi

# ── 3. Node.js (optional) ─────────────────────────────────────────────────────
section "Node.js"

if command -v node &>/dev/null; then
    success "Node.js already installed ($(node --version)), npm $(npm --version)"
else
    warn "Node.js (npm) is not installed."
    if ask "Install Node.js LTS?"; then
        case "$SYS_MGR" in
            apt)
                info "Adding NodeSource LTS repository..."
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            pacman) sys_install nodejs npm ;;
            dnf)    sys_install nodejs npm ;;
            *)
                error "Cannot auto-install Node.js. Install manually: https://nodejs.org"
                ;;
        esac
        if command -v node &>/dev/null; then
            success "Node.js installed ($(node --version)), npm $(npm --version)"
        else
            error "Node.js installation failed. Install manually: https://nodejs.org"
        fi
    else
        info "Skipping Node.js. Install later: https://nodejs.org"
        info "  lpm install <pkg> --node  will remind you if npm is missing."
    fi
fi

# ── 4. Dart (optional) ────────────────────────────────────────────────────────
section "Dart"

if command -v dart &>/dev/null; then
    success "Dart already installed ($(dart --version 2>&1))"
else
    warn "Dart is not installed."
    if ask "Install Dart?"; then
        case "$SYS_MGR" in
            apt)
                info "Adding Dart apt repository..."
                sudo apt-get install -y apt-transport-https gnupg
                wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub \
                    | sudo gpg --dearmor -o /usr/share/keyrings/dart.gpg
                echo 'deb [signed-by=/usr/share/keyrings/dart.gpg arch=amd64] https://storage.googleapis.com/download.dartlang.org/linux/debian stable main' \
                    | sudo tee /etc/apt/sources.list.d/dart_stable.list
                sudo apt-get update
                sudo apt-get install -y dart
                DART_BIN="/usr/lib/dart/bin"
                PUB_BIN="$HOME/.pub-cache/bin"
                for RC in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
                    if [ -f "$RC" ] && ! grep -q 'pub-cache' "$RC"; then
                        printf '\n# Dart\nexport PATH="$PATH:%s:%s"\n' "$DART_BIN" "$PUB_BIN" >> "$RC"
                    fi
                done
                export PATH="$PATH:$DART_BIN:$PUB_BIN"
                ;;
            pacman)
                if command -v yay &>/dev/null; then
                    yay -S --noconfirm dart
                elif command -v paru &>/dev/null; then
                    paru -S --noconfirm dart
                else
                    error "AUR helper (yay/paru) not found. Install Dart manually: https://dart.dev/get-dart"
                fi
                ;;
            dnf)
                error "No official Dart RPM repo. Install Flutter SDK (includes Dart): https://docs.flutter.dev/get-started/install/linux"
                ;;
            *)
                error "Cannot auto-install Dart. Install manually: https://dart.dev/get-dart"
                ;;
        esac
        if command -v dart &>/dev/null; then
            success "Dart installed ($(dart --version 2>&1))"
        else
            warn "Dart installation may have failed. Verify: dart --version"
        fi
    else
        info "Skipping Dart. Install later: https://dart.dev/get-dart"
        info "  lpm install <pkg> --dart  will remind you if dart is missing."
    fi
fi

# ── 5. Install LPM itself ─────────────────────────────────────────────────────
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

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}LPM Installer  v1.2.0${NC}"
echo -e "${BOLD}${GREEN}✅  LPM installation complete!${NC}"
echo "────────────────────────────────────────────────────"
echo -e "  ${CYAN}lpm install <pkg> -- python${NC}              → Python (pip)"
echo -e "  ${CYAN}lpm install <pkg> --rust${NC}       → Rust   (cargo)"
echo -e "  ${CYAN}lpm install <pkg> --node${NC}       → Node   (npm -g)"
echo -e "  ${CYAN}lpm install <pkg> --dart${NC}       → Dart   (pub global)"
echo -e "  ${CYAN}lpm install <pkg> --cpp${NC}        → C++    (apt/pacman/dnf)"
echo -e "  ${CYAN}lpm install <pkg> --local${NC}      → install into current project"
echo -e "  ${CYAN}lpm remove  <pkg> [--flag]${NC}     → remove"
echo -e "  ${CYAN}lpm list${NC}                       → show registry"
echo -e "  ${CYAN}lpm updates${NC}                    → check for new version"
echo "────────────────────────────────────────────────────"
