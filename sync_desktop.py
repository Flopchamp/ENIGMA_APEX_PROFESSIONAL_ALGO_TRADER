"""
sync_desktop.py — Sync root Python files into ENIGMA_APEX_DESKTOP_CLEAN/

Run this after any code change to keep the desktop distribution up to date:
    python sync_desktop.py

ENIGMA_APEX_DESKTOP_CLEAN/ is a standalone distribution snapshot for desktop
users. Its Python files must always mirror the root; only its .bat launchers,
READMEs, and config files are desktop-specific and are never overwritten here.
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DEST = ROOT / "ENIGMA_APEX_DESKTOP_CLEAN"


def sync():
    synced, skipped, errors = 0, 0, 0

    for dest_py in sorted(DEST.rglob("*.py")):
        # Relative path from DEST  →  corresponding root file
        rel = dest_py.relative_to(DEST)
        src = ROOT / rel

        if not src.exists():
            print(f"  SKIP  (no root counterpart): {rel}")
            skipped += 1
            continue

        try:
            shutil.copy2(src, dest_py)
            print(f"  SYNC  {rel}")
            synced += 1
        except OSError as e:
            print(f"  ERROR {rel}: {e}")
            errors += 1

    print()
    print(f"Done: {synced} synced, {skipped} skipped, {errors} errors")
    return errors == 0


if __name__ == "__main__":
    print(f"Syncing root -> {DEST.name}/\n")
    ok = sync()
    raise SystemExit(0 if ok else 1)
