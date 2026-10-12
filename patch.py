#!/usr/bin/env python3
"""Deprecated entry point. The patcher now lives in the `nexus` package.

Kept so `python3 patch.py check --src ...` keeps working.

    python3 nexus.py check  --src <tree>
    python3 nexus.py apply  --src <tree>
    python3 nexus.py revert --src <tree>
    python3 nexus.py ids    --src <tree>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nexus.cli import main  # noqa: E402

if __name__ == "__main__":
    print("note: patch.py is a shim; the implementation is now the nexus package. "
          "Use nexus.py directly. The original single-file version is kept at "
          "legacy/patch.py for reference.", file=sys.stderr)
    sys.exit(main())