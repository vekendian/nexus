"""Nexus patcher internals.

Split from the original single-file ``patch.py`` (kept at ``legacy/patch.py``
as a reference implementation). Importing this package is side-effect free so
the test suite needs no apktool tree on disk.
"""

__all__ = ["anchors", "ids", "tree"]
__version__ = "2.0.0"