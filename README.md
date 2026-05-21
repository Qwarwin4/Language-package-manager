# LPM — Universal Package Manager Wrapper

[![Lint & Test](https://github.com/YOUR_USERNAME/lpm/actions/workflows/lint.yml/badge.svg)](https://github.com/YOUR_USERNAME/lpm/actions)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

LPM is a unified CLI for installing packages across **Python, Rust, Node.js, Dart and C++** — both globally and locally inside a project.

---

## Installation

```bash
git clone https://github.com/Qwarwin4/Language-package-manager.git
cd Language-package-manager
chmod +x install.sh
./install.sh
```

`install.sh` will ask whether to install any missing runtimes (Rust, Node.js, Dart) — each one is optional. After that it drops the `lpm` command into `/usr/local/bin`.

---

## Uninstall

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Removes LPM itself (`/opt/lpm` and the `lpm` symlink). Language runtimes are **not** touched.

---

## Usage

> **A language flag is always required** for `install` and `remove`. Without it lpm doesn't know which package manager to use.

### Install globally

| Command | Tool used |
|---|---|
| `lpm install <pkg> --python` | pip |
| `lpm install <pkg> --rust` | cargo install |
| `lpm install <pkg> --node` | npm install -g |
| `lpm install <pkg> --dart` | dart pub global activate |
| `lpm install <pkg> --cpp` | apt / pacman / dnf |

### Install locally (`--local`)

Installs into the **current project directory** instead of globally. Navigate to your project folder first, then run:

| Command | What happens |
|---|---|
| `lpm install <pkg> --python --local` | creates `.venv/`, installs with pip |
| `lpm install <pkg> --rust --local` | runs `cargo add` (edits `Cargo.toml`) |
| `lpm install <pkg> --node --local` | runs `npm install` (into `node_modules/`) |
| `lpm install <pkg> --dart --local` | runs `dart pub add` (edits `pubspec.yaml`) |
| `lpm install <pkg> --cpp --local` | creates `conanfile.txt`, runs `conan install` |

### Remove globally

```bash
lpm remove <pkg> --python
lpm remove <pkg> --rust
lpm remove <pkg> --node
lpm remove <pkg> --dart
lpm remove <pkg> --cpp
```

### Remove locally

Navigate to the project folder first, then pass `--local` along with the language flag:

```bash
lpm remove <pkg> --python --local
lpm remove <pkg> --rust   --local
lpm remove <pkg> --node   --local
lpm remove <pkg> --dart   --local
```

### Other commands

```bash
lpm list        # show all packages tracked by lpm
lpm updates     # check GitHub for a newer version
lpm --version   # print current version
```

---

## Examples

```bash
# Python
lpm install requests --python
lpm install requests --python --local   # into .venv in current directory
lpm remove  requests --python
lpm remove  requests --python --local

# Rust
lpm install tokio --rust
lpm install tokio --rust --local        # cargo add into Cargo.toml
lpm remove  tokio --rust

# Node.js
lpm install typescript --node
lpm install typescript --node --local   # npm install into node_modules
lpm remove  typescript --node
lpm remove  typescript --node --local

# Dart
lpm install dart_style --dart
lpm install dart_style --dart --local   # dart pub add into pubspec.yaml
lpm remove  dart_style --dart

# C++
lpm install boost --cpp
lpm install boost --cpp --local         # conan install into ./build
lpm remove  boost --cpp
```

---

## Supported distros

| Distro | Package manager |
|---|---|
| Ubuntu, Debian, Kali, Mint | apt |
| Arch, Manjaro | pacman |
| Fedora, CentOS, RHEL | dnf |


## Contributing

1. Fork → feature branch → PR
2. `shellcheck install.sh uninstall.sh` must pass
3. `pyflakes main.py pypi_handler.py utils.py` must pass

---

## License

MIT — see [LICENCE](LICENCE).
````

**Topics:**
`package-manager` `python` `rust` `nodejs` `dart` `cpp` `linux` `cli` `pip` `cargo` `npm`
