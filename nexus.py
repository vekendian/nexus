#!/usr/bin/env python3
"""Nexus patcher entry point.

    nexus.py check  --src <tree>    verify anchors + IDs, read-only
    nexus.py apply  --src <tree>    write a patched copy to <tree>_nexus_output
    nexus.py ids    --src <tree>    show the ID lock file and audit it

Run `bash build.sh --src <tree>_nexus_output` afterwards to produce a signed APK.

Note: this file and the `nexus/` package share a name in the same directory.
That is fine — running `python3 nexus.py` executes this file as __main__, so
`import nexus` still resolves to the package and nothing recurses.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nexus.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())