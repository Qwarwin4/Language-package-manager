import urllib.request
import urllib.error
import json
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────
# Change these two lines to match your GitHub repo before publishing
GITHUB_USER = "Qwarwin4"
GITHUB_REPO = "lpm"

API_URL      = f"https://api.github.com/repos/{Qwarwin4}/{lpm}/releases/latest"
RELEASES_URL = f"https://github.com/{lpm}/{lpm}/releases"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_version(tag: str) -> tuple:
    """'v1.2.0' or '1.2.0'  →  (1, 2, 0)"""
    tag = tag.lstrip("v")
    try:
        return tuple(int(x) for x in tag.split("."))
    except ValueError:
        return (0,)


def fetch_latest_release() -> dict | None:
    """
    Returns a dict with keys:
        tag        – version string from GitHub, e.g. 'v1.3.0'
        version    – stripped, e.g. '1.3.0'
        url        – HTML page of the release
        notes      – first 300 chars of the release body (may be empty)
        published  – ISO date string
    Returns None on any network / parse error.
    """
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept":     "application/vnd.github+json",
            "User-Agent": f"lpm-updater/{GITHUB_USER}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Repo has no releases yet
            return None
        raise
    except Exception:
        return None

    tag = data.get("tag_name", "")
    return {
        "tag":       tag,
        "version":   tag.lstrip("v"),
        "url":       data.get("html_url", RELEASES_URL),
        "notes":     (data.get("body") or "")[:300].strip(),
        "published": (data.get("published_at") or "")[:10],
    }


def check_updates(current_version: str) -> None:
    """
    Called by `lpm updates`.
    Prints a human-readable update report to stdout.
    """
    from utils import log_info, log_success, log_warn, log_error, Colors

    log_info(f"Current version : v{current_version}")
    log_info(f"Checking        : {API_URL}")
    print()

    release = fetch_latest_release()

    if release is None:
        log_warn("Could not reach GitHub. Check your internet connection.")
        log_info(f"You can check manually: {RELEASES_URL}")
        return

    current_tuple = _parse_version(current_version)
    latest_tuple  = _parse_version(release["tag"])

    if latest_tuple > current_tuple:
        print(f"{Colors.WARNING}{'─'*48}{Colors.ENDC}")
        print(f"{Colors.WARNING}  ⬆  Update available!{Colors.ENDC}")
        print(f"{Colors.WARNING}     v{current_version}  →  {release['tag']}  "
              f"(released {release['published']}){Colors.ENDC}")
        print(f"{Colors.WARNING}{'─'*48}{Colors.ENDC}")
        if release["notes"]:
            print(f"\n{Colors.OKCYAN}Release notes:{Colors.ENDC}")
            for line in release["notes"].splitlines():
                print(f"  {line}")
        print(f"\n{Colors.OKBLUE}Download / changelog:{Colors.ENDC}")
        print(f"  {release['url']}")
        print()
        print("To update, run:")
        print(f"  cd /path/to/lpm && git pull && ./install.sh")

    elif latest_tuple == current_tuple:
        log_success(f"You are up to date! (v{current_version})")
        print(f"  {RELEASES_URL}")

    else:
        # local version is newer — dev / pre-release build
        log_info(
            f"Your build (v{current_version}) is ahead of the latest "
            f"release ({release['tag']}). Looks like a dev build."
        )


# ── Standalone usage ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Allow quick CLI test:  python3 updater.py 1.2.0
    current = sys.argv[1] if len(sys.argv) > 1 else "0.0.0"
    check_updates(current)
