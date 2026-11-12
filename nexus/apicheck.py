"""Resolve every framework method the injected smali calls.

Two runtime-only failure classes have shipped from this patcher, and neither
is visible to `apktool b` or to an arity check:

    java.lang.VerifyError: invalid argument count (7) exceeds outsSize (6)
        -> register count wrong; fixed by tests/test_invoke_arity.py

    java.lang.NoSuchMethodError: No direct method
        <init>(Landroid/content/Context;Ljava/lang/Class;)Landroid/content/Intent;
        -> the callee does not resolve

So every `invoke` in the patched smali is resolved against
tools/android-34.jar (or framework/android-34.jar beside the checkout): the
class must be in the archive, and the exact
`name+descriptor` pair must be declared by it. Class-file constant pools are
parsed directly, which yields the real dex descriptors without needing javap
per class.

Scope and limits, stated plainly:

  * Resolves framework calls only. Calls into GameGuardian's own obfuscated
    classes are skipped -- those are verified by the arity audit and by running
    the app, not by anything on this machine.
  * android.jar is API 34; the device runs API 36. A member present in 34 but
    absent from 36 passes here and can still fail on device. That is exactly
    what happened with Intent(Context, Class): it is in android.jar and was
    rejected at runtime. The audit catches typos and wrong descriptors, not
    platform drift.
"""

from __future__ import annotations

import re
import struct
import zipfile
from functools import lru_cache
from pathlib import Path

# The jar ships in tools/; a developer checkout that keeps it beside the repo
# (framework/) still resolves through the fallback, so no absolute path is
# baked in and a fresh clone works on any machine.
_TOOLS = Path(__file__).resolve().parents[1] / "tools/android-34.jar"
_SIBLING = Path(__file__).resolve().parents[2] / "framework/android-34.jar"
ANDROID_JAR = _TOOLS if _TOOLS.is_file() else _SIBLING

# The full descriptor must be rebuilt from all three parts; dropping the
# return type silently turns every lookup into a miss.
INVOKE_RE = re.compile(
    r"^\s*(invoke-\S+)\s*\{[^}]*\},\s*(L[^;]+;)->(\S+?)\(([^)]*)\)(.*)$")
METHOD_RE = re.compile(r"^\.method[ \t]+(.*)$", re.M)

# Constant-pool tags and the byte length that follows each tag. Long (5) and
# Double (6) occupy TWO pool slots each, which `taken` accounts for below.
_CP_FIXED = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4,
             12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
_CP_TWO_SLOTS = (5, 6)


@lru_cache(maxsize=1)
def _jar():
    if not ANDROID_JAR.is_file():
        return None
    return zipfile.ZipFile(ANDROID_JAR)


def _utf8(cp: dict, i: int) -> str:
    return cp[i][1]


def _read_pool(data: bytes):
    """Return ({index: (tag, value)}, end_offset) for a class file's pool.

    `data` is the whole file: skip magic (4), minor+major version (4) and the
    constant_pool_count (2) before the pool itself, which starts at offset 10.
    The end offset matters -- everything after the pool is indexed from it.
    """
    n = struct.unpack_from(">H", data, 8)[0]
    cp = {}
    i = 10
    slot = 1                       # pool indices are 1-based; Long/Double eat two
    while slot < n:
        tag = data[i]
        if tag == 1:
            ln = struct.unpack_from(">H", data, i + 1)[0]
            cp[slot] = (tag, data[i + 3:i + 3 + ln].decode("utf-8", "replace"))
            i += 3 + ln
        elif tag in _CP_FIXED:
            cp[slot] = (tag, data[i + 1:i + 1 + _CP_FIXED[tag]])
            i += 1 + _CP_FIXED[tag]
        else:
            return None, 0
        slot += 2 if tag in _CP_TWO_SLOTS else 1
    return cp, i


def _skip_interfaces(data: bytes, off: int) -> int:
    """interfaces_table is a count plus bare u2 class indices -- NOT member_info."""
    n = struct.unpack_from(">H", data, off)[0]
    return off + 2 + 2 * n


def _skip_members(data: bytes, off: int, cp: dict) -> int:
    count = struct.unpack_from(">H", data, off)[0]
    off += 2
    for _ in range(count):
        off += 6                                   # access, name, descriptor
        attrs = struct.unpack_from(">H", data, off)[0]
        off += 2
        for _ in range(attrs):
            ln = struct.unpack_from(">I", data, off + 2)[0]
            off += 6 + ln
    return off


def _slash(name: str) -> str:
    """'Landroid/content/Intent;' -> 'android/content/Intent'."""
    return name[1:-1] if name.startswith("L") and name.endswith(";") else name


@lru_cache(maxsize=4096)
def _own_members(class_name: str):
    """(declared {(name, desc)}, superclass name or None) for one class."""
    z = _jar()
    if z is None:
        return None
    try:
        data = z.read(_slash(class_name) + ".class")
    except KeyError:
        return None
    if data[:4] != b"\xca\xfe\xba\xbe":
        return None
    cp, off = _read_pool(data)
    if not cp:
        return None
    _access, this_i, super_i = struct.unpack_from(">HHH", data, off)
    off += 6                       # access_flags, this_class, super_class

    def resolve(idx):
        if idx == 0:
            return None
        name_i = struct.unpack_from(">H", cp[idx][1], 0)[0]
        return "L" + cp[name_i][1] + ";"

    off = _skip_interfaces(data, off)             # interfaces_table
    off = _skip_members(data, off, cp)            # fields
    mcount = struct.unpack_from(">H", data, off)[0]
    off += 2
    out = set()
    for _ in range(mcount):
        _access, name_i, desc_i = struct.unpack_from(">HHH", data, off)
        off += 6
        out.add((cp[name_i][1], cp[desc_i][1]))
        attrs = struct.unpack_from(">H", data, off)[0]
        off += 2
        for _ in range(attrs):
            ln = struct.unpack_from(">I", data, off + 2)[0]
            off += 6 + ln
    return out, resolve(super_i)


@lru_cache(maxsize=4096)
def declared_methods(class_name: str):
    """{(name, descriptor)} for a framework class AND its superclasses.

    The walk matters: Button.setBackgroundResource and AlertDialog.getContext
    are declared on View and Dialog respectively, not on the classes our smali
    names. Resolving only the named class reports them as missing.
    """
    seen = set()
    out = set()
    cur = class_name
    while cur and cur not in seen:
        seen.add(cur)
        got = _own_members(cur)
        if got is None:
            break
        members, sup = got
        out |= members
        cur = sup
    return out or None


def unresolved(src: str):
    """(method, line, reason) for framework calls that do not resolve."""
    z = _jar()
    if z is None:
        return []
    classes = {entry[:-6] for entry in z.namelist() if entry.endswith(".class")}
    out = []
    for m in METHOD_RE.finditer(src):
        body_start = src.index("\n", m.end())
        end = src.find("\n.end method", body_start)
        for line in (l.strip() for l in src[body_start:end if end != -1 else len(src)].splitlines()):
            g = INVOKE_RE.match(line)
            if not g:
                continue
            _op, cls, name, params, ret = g.groups()
            # A class file's method descriptor excludes the method name:
            # NameAndType holds "(params)return", and the name is separate.
            desc = f"({params}){ret}"
            if _slash(cls) not in classes:
                continue                              # not a framework class
            methods = declared_methods(cls)
            if methods is None:
                out.append((m.group(1), line, f"{cls} not found in android.jar"))
            elif (name, desc) not in methods:
                out.append((m.group(1), line,
                            f"{cls} has no {name}{desc}"))
    return out


def _fmt(problems, rel):
    return "\n".join(f"{rel}: {m}: {why}\n    {line}" for m, line, why in problems)
