#!/usr/bin/env python3
"""Nexus patcher entry point.

    nexus.py check  --src <tree>    verify anchors + IDs, read-only
    nexus.py apply  --src <tree>    patch the tree (backed up first)
    nexus.py revert --src <tree>    restore from the backup
    nexus.py ids    --src <tree>    show the ID lock file and audit it

Run `./build.sh --src <tree>` afterwards to produce a signed APK.

Note: this file and the `nexus/` package share a name in the same directory.
That is fine — running `python3 nexus.py` executes this file as __main__, so
`import nexus` still resolves to the package and nothing recurses.

The original single-file implementation is kept at legacy/patch.py as a
reference for diffing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nexus.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())