"""
state.py — Gist-backed state persistence.
Reusable by any account that needs to persist data across GitHub Actions runs.

Falls back to a local JSON file when GIST_ID is not set (useful for local dev).
"""

import json, os, requests

GIST_ID   = os.environ.get("GIST_ID",  "")
GH_TOKEN  = os.environ.get("GH_TOKEN", "")


def load_state(filename, dry_run=False):
    """Load state dict from Gist (or local file in dry-run / no-Gist mode)."""
    if dry_run or not GIST_ID:
        if os.path.exists(filename):
            with open(filename) as f:
                data = json.load(f)
                return data if data else None
        return None

    r = requests.get(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"Bearer {GH_TOKEN}"},
    )
    r.raise_for_status()
    files = r.json().get("files", {})
    if filename not in files:
        return None
    data = json.loads(files[filename]["content"])
    return data if data else None


def save_state(state, filename, dry_run=False):
    """Save state dict to Gist (or local file in dry-run / no-Gist mode)."""
    if dry_run or not GIST_ID:
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        print(f"  State saved → local {filename}")
        return

    r = requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"Bearer {GH_TOKEN}"},
        json={"files": {filename: {"content": json.dumps(state, indent=2)}}},
    )
    r.raise_for_status()
    print(f"  State saved → Gist ({filename})")
