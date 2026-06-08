# LPM — Universal Package Manager Wrapper

[![Lint & Test](https://github.com/Qwarwin4/Language-package-manager/actions/workflows/lint.yml/badge.svg)](https://github.com/Qwarwin4/Language-package-manager/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

LPM is a unified CLI for installing packages across **Python and C++** — both globally and locally inside a project.

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/lpm.git
cd lpm
chmod +x install.sh
./install.sh
```

After that the `lpm` command is available globally via `/usr/local/bin`.

---

## Uninstall

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Removes LPM itself (`/opt/lpm` and the `lpm` symlink). Your toolchains are **not** touched.

---

## Usage

> **A language flag is always required** for `install` and `remove`.

### Install globally

| Command | Tool used |
|---|---|
| `lpm install <pkg> --python` | pip |
| `lpm install <pkg> --cpp` | apt / pacman / dnf |

### Install locally (`--local`)

Installs into the **current project directory**. Navigate to your project folder first.

| Command | What happens |
|---|---|
| `lpm install <pkg> --python --local` | creates `.venv/`, installs with pip |
| `lpm install <pkg> --cpp --local` | creates `conanfile.txt`, runs `conan install` |

### Remove globally

```bash
lpm remove <pkg> --python
lpm remove <pkg> --cpp
```

### Remove locally

Navigate to the project folder first, then:

```bash
lpm remove <pkg> --python --local
lpm remove <pkg> --cpp    --local
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

---

## Project structure

```
lpm/
├── main.py           # CLI entry point + language handlers
├── pypi_handler.py   # PyPI REST API client
├── updater.py        # GitHub release checker
├── utils.py          # Coloured logging helpers
├── packages.json     # System package name mappings
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
