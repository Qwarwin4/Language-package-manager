# LPM — Universal Package Manager Wrapper

[![Lint & Test](https://github.com/Qwarwin4/lpm/actions/workflows/lint.yml/badge.svg)](https://github.com/Qwarwin4/lpm/actions)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

LPM is a unified CLI for installing packages across **Python, Rust, Node.js, Dart and C++** — both globally and locally inside a project.

---

## Installation

```bash
git clone https://github.com/Qwarwin4/lpm.git
cd lpm
chmod +x install.sh
./install.sh
```

`install.sh` automatically installs any missing runtimes (Rust via rustup, Node via NodeSource, Dart via the official apt repo) and drops the `lpm` command into `/usr/local/bin`.

---

## Uninstall

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Interactive prompts let you choose whether to remove each runtime as well.

---

## Usage

### Global install (default)

| Command | Tool used |
|---|---|
| `lpm install <pkg> -- python` | pip |
| `lpm install <pkg> --rust` | cargo install |
| `lpm install <pkg> --node` | npm install -g |
| `lpm install <pkg> --dart` | dart pub global activate |
| `lpm install <pkg> --cpp` | apt / pacman / dnf |

### Local install (`--local`)

Installs into the **current project directory** instead of globally.

| Command | What happens |
|---|---|
| `lpm install <pkg> --python --local` | creates `.venv/`, installs with pip |
| `lpm install <pkg> --rust --local` | runs `cargo add` (edits `Cargo.toml`) |
| `lpm install <pkg> --node --local` | runs `npm install` (into `node_modules/`) |
| `lpm install <pkg> --dart --local` | runs `dart pub add` (edits `pubspec.yaml`) |
| `lpm install <pkg> --cpp --local` | creates `conanfile.txt`, runs `conan install` |

### Remove

```bash
lpm remove <pkg>               # global
lpm remove <pkg> --local       # local project
lpm remove <pkg> --rust
lpm remove <pkg> --node --local
# etc.
```

### List

```bash
lpm list
```

---

## Supported distros

| Distro | Package manager |
|---|---|
| Ubuntu, Debian, Kali, Mint | apt |
| Arch, Manjaro | pacman |
| Fedora, CentOS, RHEL | dnf |

---

## Project structure

```
lpm/
├── main.py           # CLI entry point + all language handlers
├── pypi_handler.py   # PyPI REST API client
├── utils.py          # Coloured logging helpers
├── packages.json     # Registry of installed packages + system mappings
├── install.sh        # System-wide installer
├── uninstall.sh      # Clean removal
└── .github/
    ├── workflows/lint.yml
    └── ISSUE_TEMPLATE/
```

---

## Contributing

1. Fork → feature branch → PR
2. `shellcheck install.sh uninstall.sh` must pass
3. `pyflakes main.py pypi_handler.py utils.py` must pass

---

## License

MIT — see [LICENCE](LICENCE).

---

One-liner for the GitHub **Description** field:

> A single CLI for pip, cargo, npm, dart pub and apt/pacman/dnf — stop remembering, start installing.

**Topics:**
`package-manager` `python` `rust` `nodejs` `dart` `cpp` `linux` `cli` `pip` `cargo` `npm`
