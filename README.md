**LPM — Universal Package Manager Wrapper**

> Tired of remembering whether it's `pip install`, `cargo install`, or `npm install -g`? LPM handles it for you.

---

**What is this?**

LPM is a thin wrapper that sits on top of your existing package managers. You run one command, it figures out the rest — which tool to call, which distro you're on, whether you want a global install or a local project dependency. Everything you install gets tracked in a single registry at `~/.lpm/packages.json`.

---

**What it supports**

- 🐍 Python — pip globally, or auto-creates a `.venv` for local installs
- 🦀 Rust — `cargo install` for binaries, `cargo add` for project dependencies
- 🟩 Node.js — `npm -g` globally, or `npm install` into the current project
- 🎯 Dart — `pub global activate` or `dart pub add`
- ⚙️ C++ — `apt` / `pacman` / `dnf` globally, or Conan for project-level deps
- 🔄 Built-in update checker via `lpm updates`
- 🏠 Works on Ubuntu, Debian, Arch, Fedora and their derivatives

---

**Getting started**

```bash
git clone https://github.com/USERNAME/lpm.git
cd lpm && ./install.sh
```

```bash
lpm install requests   --python
lpm install tokio      --rust
lpm install typescript --node
lpm install dart_style --dart
lpm install boost      --cpp

lpm install numpy --python --local   # installs into .venv in current directory
lpm list
lpm updates
```

---

One-liner for the GitHub **Description** field:

> A single CLI for pip, cargo, npm, dart pub and apt/pacman/dnf — stop remembering, start installing.

**Topics:**
`package-manager` `python` `rust` `nodejs` `dart` `cpp` `linux` `cli` `pip` `cargo` `npm`
