import os
import subprocess
import sys
import json
import argparse
import distro
from pypi_handler import PyPIHandler
from utils import log_info, log_success, log_error, log_warn, log_action, Colors

VERSION = "1.0-br1"

class LPM:
    def __init__(self):
        self.distro_id = distro.id()
        self.manager   = self._get_manager()
        lpm_dir = os.path.join(os.path.expanduser('~'), '.lpm')
        os.makedirs(lpm_dir, exist_ok=True)
        self.db_path   = os.path.join(lpm_dir, 'packages.json')
        self.data      = self._load_db()
        self.pypi      = PyPIHandler()
        self.cwd       = os.getcwd()

    # ── Distro detection ──────────────────────────────────────────────────────

    def _get_manager(self):
        mapping = {
            'ubuntu': 'apt', 'debian': 'apt', 'kali': 'apt', 'mint': 'apt',
            'arch':   'pacman', 'manjaro': 'pacman',
            'fedora': 'dnf',  'centos':  'dnf',  'rhel': 'dnf'
        }
        mgr = mapping.get(self.distro_id)
        if not mgr:
            if distro.like('debian'):                          mgr = 'apt'
            elif distro.like('arch'):                          mgr = 'pacman'
            elif distro.like('fedora') or distro.like('rhel'): mgr = 'dnf'
            else:                                              mgr = 'unknown'
        log_info(f"Detected Distro: {self.distro_id.upper()} | Manager: {mgr}")
        return mgr

    # ── DB ────────────────────────────────────────────────────────────────────

    def _load_db(self):
        empty = {"mapping": {}, "installed": {"python": [], "cpp": [], "rust": [], "node": [], "dart": []}}
        if not os.path.exists(self.db_path):
            log_warn("DB not found. Creating new packages.json...")
            with open(self.db_path, 'w') as f:
                json.dump(empty, f, indent=4)
            return empty
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            for lang in ("python", "cpp", "rust", "node", "dart"):
                data.setdefault("installed", {}).setdefault(lang, [])
            return data
        except json.JSONDecodeError:
            log_error("Corrupted JSON DB. Resetting...")
            return empty

    def _save_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def _record_package(self, pkg_name, category):
        if pkg_name not in self.data['installed'][category]:
            self.data['installed'][category].append(pkg_name)
            self._save_db()
            log_success(f"Registered '{pkg_name}' in [{category}]")

    def _unrecord_package(self, pkg_name, category):
        if pkg_name in self.data['installed'][category]:
            self.data['installed'][category].remove(pkg_name)
            self._save_db()

    # ── Shell helpers ─────────────────────────────────────────────────────────

    def _execute(self, cmd, cwd=None):
        log_action(cmd)
        try:
            subprocess.run(cmd, shell=True, check=True, cwd=cwd)
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"Command failed with code {e.returncode}")
            return False

    def _check_tool(self, tool):
        return subprocess.run(f"command -v {tool}", shell=True, capture_output=True).returncode == 0

    def _confirm_force(self, pkg_name, lang):
        log_warn(f"Package '{pkg_name}' not in lpm registry ({lang}).")
        return input("Force remove anyway? (y/n): ").strip().lower() == 'y'

    # ── Python ────────────────────────────────────────────────────────────────

    def install_python(self, pkg_name, local=False):
        if local:
            venv_dir = os.path.join(self.cwd, '.venv')
            if not os.path.isdir(venv_dir):
                log_info(f"Creating virtualenv at {venv_dir} ...")
                if not self._execute(f"python3 -m venv {venv_dir}"):
                    return
            pip = os.path.join(venv_dir, 'bin', 'pip')
            log_info(f"Installing '{pkg_name}' into local venv ({venv_dir}) ...")
            if self._execute(f"{pip} install {pkg_name}"):
                self._record_package(pkg_name, 'python')
                log_info(f"Activate with: source {venv_dir}/bin/activate")
            return

        log_info(f"Checking PyPI for '{pkg_name}'...")
        if self.pypi.package_exists(pkg_name):
            info = self.pypi.get_package_info(pkg_name)
            if info:
                log_success(f"Found on PyPI! v{info['version']} - {info['summary'][:50]}...")
            cmd = f"pip install {pkg_name}"
            if sys.prefix == sys.base_prefix:
                log_warn("System Python detected. PEP 668 protection active.")
                choice = input(f"{Colors.WARNING}Use --break-system-packages? (y/n): {Colors.ENDC}")
                if choice.lower() != 'y':
                    log_info("Cancelled. Tip: use --local to install into a project venv.")
                    return
                cmd += " --break-system-packages"
            if self._execute(cmd):
                self._record_package(pkg_name, 'python')
        else:
            log_warn("Not found on PyPI. Checking local mapping for system package...")
            pkg_info = self.data['mapping'].get(pkg_name.lower())
            if pkg_info and self.manager in pkg_info:
                target_pkg = pkg_info[self.manager]
                log_info(f"Found system mapping: {target_pkg}")
                if self._install_system_pkg(target_pkg):
                    self._record_package(pkg_name, 'python')
            else:
                log_error(f"Package '{pkg_name}' not found anywhere.")

    def remove_python(self, pkg_name, local=False):
        if local:
            venv_dir = os.path.join(self.cwd, '.venv')
            pip = os.path.join(venv_dir, 'bin', 'pip')
            if not os.path.isfile(pip):
                log_error(f"No local venv found at {venv_dir}")
                return
            if self._execute(f"{pip} uninstall -y {pkg_name}"):
                self._unrecord_package(pkg_name, 'python')
                log_success(f"Removed '{pkg_name}' from local venv")
            return

        if pkg_name not in self.data['installed']['python']:
            if not self._confirm_force(pkg_name, 'Python'): return
        cmd = f"pip uninstall -y {pkg_name}"
        if sys.prefix == sys.base_prefix:
            cmd += " --break-system-packages"
        if self._execute(cmd):
            self._unrecord_package(pkg_name, 'python')
            log_success(f"Removed '{pkg_name}'")

    # ── C++ ───────────────────────────────────────────────────────────────────

    def _install_system_pkg(self, target_pkg):
        if self.manager == 'unknown':
            log_error("Unsupported distribution.")
            return False
        cmds = {
            'apt':    f"sudo apt update && sudo apt install -y {target_pkg}",
            'pacman': f"sudo pacman -S --noconfirm {target_pkg}",
            'dnf':    f"sudo dnf install -y {target_pkg}",
        }
        cmd = cmds.get(self.manager)
        return self._execute(cmd) if cmd else False

    def install_cpp(self, pkg_name, local=False):
        if local:
            if not self._check_tool("conan"):
                log_warn("conan not found. Installing via pip...")
                self._execute("pip install conan --break-system-packages 2>/dev/null || pip install conan")
            conanfile = os.path.join(self.cwd, 'conanfile.txt')
            if not os.path.isfile(conanfile):
                log_info(f"Creating minimal conanfile.txt in {self.cwd} ...")
                with open(conanfile, 'w') as f:
                    f.write(f"[requires]\n{pkg_name}/[*]\n\n[generators]\nCMakeDeps\nCMakeToolchain\n")
            build_dir = os.path.join(self.cwd, 'build')
            os.makedirs(build_dir, exist_ok=True)
            log_info(f"Running conan install for '{pkg_name}' into {build_dir} ...")
            if self._execute(f"conan install {self.cwd} --output-folder={build_dir} --build=missing", cwd=self.cwd):
                self._record_package(pkg_name, 'cpp')
            return

        pkg_info   = self.data['mapping'].get(pkg_name.lower())
        target_pkg = pkg_info[self.manager] if (pkg_info and self.manager in pkg_info) else pkg_name
        log_info(f"Installing C++ library: {target_pkg}")
        if self._install_system_pkg(target_pkg):
            self._record_package(pkg_name, 'cpp')

    def remove_cpp(self, pkg_name, local=False):
        if local:
            conanfile = os.path.join(self.cwd, 'conanfile.txt')
            if os.path.isfile(conanfile):
                log_warn(f"Remove '{pkg_name}' from {conanfile} manually, then re-run conan install.")
            else:
                log_error("No conanfile.txt found in current directory.")
            return

        if pkg_name not in self.data['installed']['cpp']:
            if not self._confirm_force(pkg_name, 'C++'): return
        pkg_info   = self.data['mapping'].get(pkg_name.lower())
        target_pkg = pkg_info[self.manager] if (pkg_info and self.manager in pkg_info) else pkg_name
        cmds = {
            'apt':    f"sudo apt remove -y {target_pkg}",
            'pacman': f"sudo pacman -Rs --noconfirm {target_pkg}",
            'dnf':    f"sudo dnf remove -y {target_pkg}",
        }
        cmd = cmds.get(self.manager)
        if cmd and self._execute(cmd):
            self._unrecord_package(pkg_name, 'cpp')
            log_success(f"Removed '{pkg_name}'")

    # ── Rust ──────────────────────────────────────────────────────────────────

    def install_rust(self, pkg_name, local=False):
        if not self._check_tool("cargo"):
            log_error("cargo not found. Run install.sh or visit https://rustup.rs")
            return
        if local:
            cargo_toml = os.path.join(self.cwd, 'Cargo.toml')
            if not os.path.isfile(cargo_toml):
                log_error(f"No Cargo.toml found in {self.cwd}. Is this a Rust project?")
                return
            log_info(f"Adding '{pkg_name}' to {cargo_toml} via cargo add ...")
            if self._execute(f"cargo add {pkg_name}", cwd=self.cwd):
                self._record_package(pkg_name, 'rust')
                log_info("Run 'cargo build' to compile.")
            return
        log_info(f"Installing Rust crate '{pkg_name}' globally via cargo install ...")
        if self._execute(f"cargo install {pkg_name}"):
            self._record_package(pkg_name, 'rust')

    def remove_rust(self, pkg_name, local=False):
        if not self._check_tool("cargo"):
            log_error("cargo not found.")
            return
        if local:
            cargo_toml = os.path.join(self.cwd, 'Cargo.toml')
            if not os.path.isfile(cargo_toml):
                log_error(f"No Cargo.toml found in {self.cwd}.")
                return
            log_info(f"Removing '{pkg_name}' from {cargo_toml} via cargo remove ...")
            if self._execute(f"cargo remove {pkg_name}", cwd=self.cwd):
                self._unrecord_package(pkg_name, 'rust')
                log_success(f"Removed '{pkg_name}' from project")
            return

        if pkg_name not in self.data['installed']['rust']:
            if not self._confirm_force(pkg_name, 'Rust'): return
        if self._execute(f"cargo uninstall {pkg_name}"):
            self._unrecord_package(pkg_name, 'rust')
            log_success(f"Removed '{pkg_name}'")

    # ── Node.js ───────────────────────────────────────────────────────────────

    def install_node(self, pkg_name, local=False):
        if not self._check_tool("npm"):
            log_error("npm not found. Run install.sh or visit https://nodejs.org")
            return
        if local:
            pkg_json = os.path.join(self.cwd, 'package.json')
            if not os.path.isfile(pkg_json):
                log_info(f"No package.json found. Running 'npm init -y' in {self.cwd} ...")
                self._execute("npm init -y", cwd=self.cwd)
            log_info(f"Installing '{pkg_name}' locally in {self.cwd} ...")
            if self._execute(f"npm install {pkg_name}", cwd=self.cwd):
                self._record_package(pkg_name, 'node')
                log_info("Installed into ./node_modules")
            return
        log_info(f"Installing Node.js package '{pkg_name}' globally via npm ...")
        if self._execute(f"npm install -g {pkg_name}"):
            self._record_package(pkg_name, 'node')

    def remove_node(self, pkg_name, local=False):
        if not self._check_tool("npm"):
            log_error("npm not found.")
            return
        if local:
            log_info(f"Removing '{pkg_name}' from local project ...")
            if self._execute(f"npm uninstall {pkg_name}", cwd=self.cwd):
                self._unrecord_package(pkg_name, 'node')
                log_success(f"Removed '{pkg_name}' from project")
            return

        if pkg_name not in self.data['installed']['node']:
            if not self._confirm_force(pkg_name, 'Node'): return
        if self._execute(f"npm uninstall -g {pkg_name}"):
            self._unrecord_package(pkg_name, 'node')
            log_success(f"Removed '{pkg_name}'")

    # ── Dart ──────────────────────────────────────────────────────────────────

    def install_dart(self, pkg_name, local=False):
        if not self._check_tool("dart"):
            log_error("dart not found. Run install.sh or visit https://dart.dev/get-dart")
            return
        if local:
            pubspec = os.path.join(self.cwd, 'pubspec.yaml')
            if not os.path.isfile(pubspec):
                log_error(f"No pubspec.yaml found in {self.cwd}. Is this a Dart/Flutter project?")
                return
            log_info(f"Adding '{pkg_name}' to pubspec.yaml via dart pub add ...")
            if self._execute(f"dart pub add {pkg_name}", cwd=self.cwd):
                self._record_package(pkg_name, 'dart')
                log_info("Run 'dart pub get' if needed.")
            return
        log_info(f"Installing Dart package '{pkg_name}' globally via pub ...")
        if self._execute(f"dart pub global activate {pkg_name}"):
            self._record_package(pkg_name, 'dart')

    def remove_dart(self, pkg_name, local=False):
        if not self._check_tool("dart"):
            log_error("dart not found.")
            return
        if local:
            pubspec = os.path.join(self.cwd, 'pubspec.yaml')
            if not os.path.isfile(pubspec):
                log_error(f"No pubspec.yaml found in {self.cwd}.")
                return
            log_info(f"Removing '{pkg_name}' from pubspec.yaml via dart pub remove ...")
            if self._execute(f"dart pub remove {pkg_name}", cwd=self.cwd):
                self._unrecord_package(pkg_name, 'dart')
                log_success(f"Removed '{pkg_name}' from project")
            return

        if pkg_name not in self.data['installed']['dart']:
            if not self._confirm_force(pkg_name, 'Dart'): return
        if self._execute(f"dart pub global deactivate {pkg_name}"):
            self._unrecord_package(pkg_name, 'dart')
            log_success(f"Removed '{pkg_name}'")

    # ── List ──────────────────────────────────────────────────────────────────

    def list_installed(self):
        icons = {'python': '🐍', 'cpp': '⚙️ ', 'rust': '🦀', 'node': '🟩', 'dart': '🎯'}
        print("\n" + "="*40)
        print(f"{Colors.BOLD}📦 LPM Registry  v{VERSION}{Colors.ENDC}")
        print("="*40)
        has_any = False
        for lang, icon in icons.items():
            pkgs = self.data['installed'].get(lang, [])
            if pkgs:
                has_any = True
                print(f"{Colors.OKCYAN}{icon} {lang.capitalize()}:{Colors.ENDC}")
                for p in pkgs:
                    print(f"  - {p}")
        if not has_any:
            print("  (Empty)")
        print("="*40 + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

LANG_FLAGS = ('--python', '--cpp', '--rust', '--node', '--dart')

def _no_lang_flag(args):
    return not any([args.python, args.cpp, args.rust, args.node, args.dart])

def main():
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}LPM v{VERSION}{Colors.ENDC} - Universal Package Manager Wrapper",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lpm install requests --python          # Python global (pip)\n"
            "  lpm install requests --python --local  # Python local  (.venv)\n"
            "  lpm install tokio    --rust             # Rust global   (cargo install)\n"
            "  lpm install tokio    --rust   --local  # Rust local    (cargo add)\n"
            "  lpm install typescript --node           # Node global   (npm -g)\n"
            "  lpm install typescript --node --local  # Node local    (npm install)\n"
            "  lpm install dart_style --dart           # Dart global   (pub global)\n"
            "  lpm install dart_style --dart --local  # Dart local    (pub add)\n"
            "  lpm install boost    --cpp              # C++ system    (apt/pacman/dnf)\n"
            "  lpm install boost    --cpp  --local    # C++ local     (conan)\n"
            "  lpm remove  requests --python          # remove global\n"
            "  lpm remove  requests --python --local  # remove from .venv\n"
            "  lpm list\n"
            "  lpm updates\n"
            "  lpm --version\n"
        )
    )
    parser.add_argument("action",   choices=["install", "remove", "list", "updates"], nargs="?",
                        help="Action to perform")
    parser.add_argument("package",  nargs="?", help="Package name")

    # Language flags — all mutually exclusive
    lang_group = parser.add_mutually_exclusive_group()
    lang_group.add_argument("--python", action="store_true",
                            help="Python package (pip / venv)")
    lang_group.add_argument("--cpp",    action="store_true",
                            help="C++ library   (apt/pacman/dnf | conan)")
    lang_group.add_argument("--rust",   action="store_true",
                            help="Rust crate    (cargo install | cargo add)")
    lang_group.add_argument("--node",   action="store_true",
                            help="Node package  (npm -g | npm install)")
    lang_group.add_argument("--dart",   action="store_true",
                            help="Dart package  (pub global | pub add)")

    parser.add_argument("--local",   action="store_true",
                        help="Install/remove inside current project directory")
    parser.add_argument("--version", action="store_true",
                        help="Show LPM version and exit")

    args = parser.parse_args()

    # --version can be called without action
    if args.version:
        print(f"lpm v{VERSION}")
        sys.exit(0)

    if not args.action:
        parser.print_help()
        sys.exit(0)

    if args.action == "list":
        LPM().list_installed()
        return

    if args.action == "updates":
        from updater import check_updates
        check_updates(VERSION)
        return

    # install / remove require a package name
    if not args.package:
        log_error("Package name required.")
        sys.exit(1)

    # install / remove require a language flag
    if _no_lang_flag(args):
        log_error(
            "Language flag required. Specify one of: "
            "--python  --rust  --node  --dart  --cpp"
        )
        log_info("Example: lpm install requests --python")
        log_info("         lpm remove  requests --python")
        sys.exit(1)

    lpm   = LPM()
    local = args.local

    if args.python:
        install_fn = lambda p: lpm.install_python(p, local)
        remove_fn  = lambda p: lpm.remove_python(p,  local)
    elif args.cpp:
        install_fn = lambda p: lpm.install_cpp(p,    local)
        remove_fn  = lambda p: lpm.remove_cpp(p,     local)
    elif args.rust:
        install_fn = lambda p: lpm.install_rust(p,   local)
        remove_fn  = lambda p: lpm.remove_rust(p,    local)
    elif args.node:
        install_fn = lambda p: lpm.install_node(p,   local)
        remove_fn  = lambda p: lpm.remove_node(p,    local)
    elif args.dart:
        install_fn = lambda p: lpm.install_dart(p,   local)
        remove_fn  = lambda p: lpm.remove_dart(p,    local)

    if args.action == "install":
        install_fn(args.package)
    elif args.action == "remove":
        remove_fn(args.package)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_warn("Operation cancelled by user.")
