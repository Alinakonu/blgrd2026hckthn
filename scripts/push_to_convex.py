"""Seed the Convex deployment from data/pins.json.

Run once after `npx convex dev` is up:
    python scripts/push_to_convex.py

Reads CONVEX_URL from the environment (or .env.local, which `convex dev`
writes automatically).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from agrisense import store  # noqa: E402

ENV_FILE = pathlib.Path(__file__).resolve().parent.parent / ".env.local"


def load_env_local():
    """Pick up CONVEX_URL from .env.local without adding a dotenv dependency."""
    import os

    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main():
    load_env_local()

    if not store.convex_url():
        print(
            "CONVEX_URL is not set.\n"
            "Run `npx convex dev` first — it writes .env.local — or export it:\n"
            "  $env:CONVEX_URL = 'https://your-deployment.convex.cloud'"
        )
        return 1

    records = store.load_local_pins()
    print(f"Pushing {len(records)} records to {store.convex_url()} ...")

    try:
        written = store.push_pins(records)
    except RuntimeError as exc:
        print(f"Failed: {exc}")
        return 1

    print(f"Wrote {written} pins.")

    remote, source = store.load_pins()
    print(f"Read back {len(remote)} pins from '{source}'.")
    if source != "convex":
        print("WARNING: read fell back to the local file — check the deployment.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
