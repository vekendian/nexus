#!/usr/bin/env bash
# Build a signed APK from a patched GameGuardian tree.
#
#   bash build.sh --src <tree> [--out nexus-1.0.0.apk]
#
# (Invoke with `bash`: Android shared storage cannot set the exec bit.)
#
# Tool paths come from the environment so this works off-device:
#   NEXUS_APKTOOL  apktool jar, or a full path   (default: apktool on PATH)
#   NEXUS_AAPT     aapt2 binary                  (default: aapt2 on PATH)
#   NEXUS_KEYSTORE signing keystore        (default: ~/.android/debug.keystore)
#   NEXUS_KEYALIAS keystore alias          (default: androiddebugkey)
#   NEXUS_KEYPASS  keystore password       (default: android)

set -euo pipefail

SRC=""
OUT="nexus-1.0.0.apk"
INTERMEDIATE="$(dirname "$OUT")/nexus_patched.apk"
ALIGNED="$(dirname "$OUT")/nexus_aligned.apk"

usage() {
    sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --src) SRC="${2:?--src needs a value}"; shift 2 ;;
        --out) OUT="${2:?--out needs a value}"; shift 2 ;;
        -h|--help) usage 0 ;;
        *) echo "unknown argument: $1" >&2; usage 1 ;;
    esac
done

[ -n "$SRC" ] || { echo "error: --src is required" >&2; usage 1; }
[ -d "$SRC" ] || { echo "error: not a directory: $SRC" >&2; exit 2; }
[ -f "$SRC/apktool.yml" ] || {
    echo "error: $SRC is not an apktool decode (no apktool.yml)" >&2; exit 2; }

APKTOOL="${NEXUS_APKTOOL:-apktool}"
AAPT="${NEXUS_AAPT:-aapt2}"
KEYSTORE="${NEXUS_KEYSTORE:-$HOME/.android/debug.keystore}"
KEYALIAS="${NEXUS_KEYALIAS:-androiddebugkey}"
KEYPASS="${NEXUS_KEYPASS:-android}"

# Fail before spending minutes on apktool if a tool is missing.
if [ ! -f "$APKTOOL" ]; then
    command -v "$APKTOOL" >/dev/null || {
        echo "error: apktool not found. Put it on PATH or set NEXUS_APKTOOL=<jar>." >&2
        exit 2
    }
fi
command -v "$AAPT"   >/dev/null || { echo "error: aapt2 not found: $AAPT" >&2; exit 2; }
# apktool only reports "Could not identify aapt binary as executable" when the
# resolved binary is a dangling symlink or has a broken shared-library link, so
# prove it actually runs before handing it a tree.
"$AAPT" version >/dev/null 2>&1 || {
    echo "error: aapt2 at '$AAPT' is present but will not run:" >&2
    echo "       $(\"$AAPT\" version 2>&1 | head -1)" >&2
    echo "       set NEXUS_AAPT=<path to a working aapt2>." >&2
    exit 2
}
command -v zipalign >/dev/null || { echo "error: zipalign not found" >&2; exit 2; }
command -v apksigner>/dev/null || { echo "error: apksigner not found" >&2; exit 2; }
[ -f "$KEYSTORE" ]  || { echo "error: keystore not found: $KEYSTORE" >&2; exit 2; }

echo "==> apktool b"
if [ -f "$APKTOOL" ]; then
    java -jar "$APKTOOL" b -f --aapt "$AAPT" "$SRC" -o "$INTERMEDIATE"
else
    "$APKTOOL" b -f --aapt "$AAPT" "$SRC" -o "$INTERMEDIATE"
fi

echo "==> zipalign"
zipalign -f 4 "$INTERMEDIATE" "$ALIGNED"

echo "==> apksigner sign"
apksigner sign --ks "$KEYSTORE" --ks-key-alias "$KEYALIAS" --ks-pass "pass:$KEYPASS" "$ALIGNED"

echo "==> verify"
apksigner verify "$ALIGNED"

cp "$ALIGNED" "$OUT"
echo
echo "Built: $OUT"
echo "Install:  adb install -r $OUT"