#!/usr/bin/env bash
# Build the Nexus module engine: Java -> smali (host) and Java -> dex (asset).
#
#   bash build-engine.sh            regenerate resources/smali + resources/res/raw
#   bash build-engine.sh --check    regenerate into build/check and diff; no writes
#                                  to resources/ -- use this to prove the committed
#                                  output still matches the sources
#
# (Invoke with `bash`: Android shared storage cannot set the exec bit.)
#
# Three source roots, compiled separately so the asset dex carries only the
# engine's own nexus.* classes and never a duplicate of the host classes:
#
#   resources/java/api      org.vekendian.nexus.api.*       -> host smali + module-api.jar
#   resources/java/host     org.vekendian.nexus.modules.* -> host smali
#   resources/java/dexexec  nexus.ExtensionRegistry + helpers -> res/raw/ydw_nexus_dexexec (dex)
#
# Tool paths come from the environment, defaulting to the jars this checkout
# ships, then to the sibling directories a developer checkout may have:
#   NEXUS_ANDROID_JAR  android.jar for javac   (tools/android-34.jar)
#   NEXUS_APKTOOL      apktool jar, for baksmali (tools/apktool-2.8.1.jar)
#   NEXUS_JAVAC        javac                  (javac 17 is fine; we target 8)
#   NEXUS_D8           d8                      (any d8 >= 3.x)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

ANDROID_JAR="${NEXUS_ANDROID_JAR:-}"
if [ -z "$ANDROID_JAR" ]; then
    ANDROID_JAR="$ROOT/tools/android-34.jar"
    [ -f "$ANDROID_JAR" ] || ANDROID_JAR="$ROOT/../framework/android-34.jar"
fi
APKTOOL="${NEXUS_APKTOOL:-}"
if [ -z "$APKTOOL" ]; then
    APKTOOL="$ROOT/tools/apktool-2.8.1.jar"
    [ -f "$APKTOOL" ] || APKTOOL="$ROOT/../tools/apktool-2.8.1.jar"
fi
JAVAC="${NEXUS_JAVAC:-javac}"
JAR="${NEXUS_JAR:-jar}"
D8="${NEXUS_D8:-d8}"

MIN_API=21
API_JAR="$ROOT/build/module-api.jar"
DEX_OUT="$ROOT/resources/res/raw/ydw_nexus_dexexec"
SMALI_OUT="$ROOT/resources/smali"
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

for tool in "$JAVAC" "$JAR"; do
    command -v "$tool" >/dev/null || { echo "error: $tool not found" >&2; exit 2; }
done
command -v "$D8" >/dev/null || { echo "error: d8 not found; set NEXUS_D8" >&2; exit 2; }
[ -f "$ANDROID_JAR" ] || {
    echo "error: android jar not found: $ANDROID_JAR" >&2
    echo "       set NEXUS_ANDROID_JAR=<path to android.jar>" >&2
    exit 2
}
if [ -f "$APKTOOL" ]; then :; else
    command -v "$APKTOOL" >/dev/null || {
        echo "error: apktool jar not found: $APKTOOL (set NEXUS_APKTOOL)" >&2
        exit 2
    }
fi

WORK="$ROOT/build/engine"
[ "$CHECK_ONLY" = 1 ] && WORK="$ROOT/build/engine-check"
rm -rf "$WORK"
mkdir -p "$WORK"/{api,host,dexexec,diag,dex,hostdex,smali,tools}

# -source 8 -target 8 keeps d8's input in a format it has always accepted. The
# android jar is on -classpath rather than -bootclasspath because JDK 17 rejects
# -bootclasspath outright; the JDK's own java.lang still supplies the core types,
# which is what every d8-based Android build does.
JAVAC_FLAGS=(-nowarn -Xlint:-options -proc:none -source 8 -target 8
             -classpath "$ANDROID_JAR" -encoding UTF-8)

echo "==> javac api"
"$JAVAC" "${JAVAC_FLAGS[@]}" -d "$WORK/api" \
    $(find resources/java/api -name '*.java')

# Each stage's -cp is the previous stage's classes PLUS the android jar: javac
# takes the last -classpath, so it has to be repeated rather than inherited.
echo "==> javac host"
"$JAVAC" "${JAVAC_FLAGS[@]}" -classpath "$WORK/api:$ANDROID_JAR" -d "$WORK/host" \
    $(find resources/java/host -name '*.java')

echo "==> javac dexexec"
"$JAVAC" "${JAVAC_FLAGS[@]}" -classpath "$WORK/api:$WORK/host:$ANDROID_JAR" \
    -d "$WORK/dexexec" \
    $(find resources/java/dexexec -name '*.java')

# The init probe. Its own source root so a build with NEXUS_DIAG=0 never ships
# an unreferenced class: javac and d8 get the register frames and reference
# types right by construction, which hand-written smali does not -- the ART
# verifier only runs on device, so a bad frame assembles cleanly and then dies
# in the Activity's onCreate.
if [ -d resources/java/diag ]; then
    echo "==> javac diag"
    "$JAVAC" "${JAVAC_FLAGS[@]}" -classpath "$WORK/api:$ANDROID_JAR" -d "$WORK/diag" \
        $(find resources/java/diag -name '*.java')
fi

echo "==> dex"
# d8 needs to SEE the host classes to reason about the interfaces the executor
# implements; without them it warns on every one of them. This d8 takes a single
# --classpath path (":"-separated lists are read as one filename), so the api and
# host output dirs go in as one jar. Only the dexexec classes are WRITTEN, so
# the asset dex never duplicates a host class.
"$JAR" --create --file "$WORK/hostlib.jar" -C "$WORK/api" . -C "$WORK/host" .

# The host is shipped as smali, so its classes go through their own dex purely
# to be disassembled. It lands in the patched tree's existing classes.dex.
# --lib android.jar: the host classes implement android/java interfaces, and d8
# wants them on the program path before it will accept the anonymous classes
# implementing Runnable or View.OnClickListener.
# Classes that ship as smali. HOST_CLASSES is collected first so the optional
# diag root can be appended without the empty directory reaching d8 when
# NEXUS_DIAG is off.
HOST_CLASSES=()
while IFS= read -r f; do HOST_CLASSES+=("$f"); done \
    < <(find "$WORK/api" "$WORK/host" -name '*.class' | sort)
if [ -d "$WORK/diag" ]; then
    while IFS= read -r f; do HOST_CLASSES+=("$f"); done \
        < <(find "$WORK/diag" -name '*.class' | sort)
fi

"$D8" --min-api "$MIN_API" --release --lib "$ANDROID_JAR" --output "$WORK/hostdex" \
    "${HOST_CLASSES[@]}"

# The executor is shipped as a dex ASSET, and must see the host classes to reason
# about the interfaces it implements -- otherwise d8 warns on every one of them.
"$D8" --min-api "$MIN_API" --release --lib "$ANDROID_JAR" \
    --classpath "$WORK/hostlib.jar" \
    --output "$WORK/dex" \
    $(find "$WORK/dexexec" -name '*.class')

echo "==> module-api.jar"
"$JAR" --create --file "$WORK/module-api.jar" -C "$WORK/api" .

echo "==> baksmali (host)"
"$JAVAC" -nowarn -proc:none -cp "$APKTOOL" -d "$WORK/tools" tools/BaksmaliDriver.java
java -cp "$WORK/tools:$APKTOOL" BaksmaliDriver "$WORK/hostdex/classes.dex" \
    "$WORK/smali" "$MIN_API" >/dev/null

if [ "$CHECK_ONLY" = 1 ]; then
    echo "==> checking committed output"
    status=0
    # Every class javac produced must be present and identical on disk.
    while IFS= read -r rel; do
        a="$WORK/smali/$rel"; b="$SMALI_OUT/$rel"
        if [ ! -f "$b" ]; then
            echo "  MISSING  $rel"; status=1
        elif ! cmp -s "$a" "$b"; then
            echo "  STALE    $rel"; status=1
        fi
    done < <(cd "$WORK/smali" && find . -name '*.smali' | sed 's|^\./||' | sort)
    # ...and nothing left behind by a class that was since deleted. Only the two
    # generated packages are considered: ModulePicker.smali is hand-written and
    # shares org/vekendian/nexus/ with them.
    while IFS= read -r rel; do
        if [ ! -f "$WORK/smali/$rel" ]; then
            echo "  ORPHAN   $rel"; status=1
        fi
    done < <(cd "$SMALI_OUT" && find org/vekendian/nexus/api org/vekendian/nexus/modules \
                 -name '*.smali' 2>/dev/null | sort)
    if [ ! -f "$SMALI_OUT/org/vekendian/nexus/ModulePicker.smali" ]; then
        echo "  MISSING  org/vekendian/nexus/ModulePicker.smali (hand-written; the"
        echo "           install step must not touch it)"; status=1
    fi
    if cmp -s "$WORK/dex/classes.dex" "$DEX_OUT"; then
        echo "  ok       res/raw/ydw_nexus_dexexec"
    else
        echo "  STALE    res/raw/ydw_nexus_dexexec"; status=1
    fi
    if [ "$status" = 0 ]; then
        echo "check ok: committed output matches the sources"
    else
        echo "check FAILED: run 'bash build-engine.sh'"
    fi
    exit "$status"
fi

echo "==> install into resources/"
# Only our two generated packages. org/vekendian/nexus/ModulePicker.smali is
# hand-written and shares the parent directory, so the packages are removed
# individually instead of wiping org/vekendian/nexus.
rm -rf "$SMALI_OUT/org/vekendian/nexus/api" "$SMALI_OUT/org/vekendian/nexus/modules"
for pkg in api modules; do
    [ -d "$WORK/smali/org/vekendian/nexus/$pkg" ] || continue
    mkdir -p "$SMALI_OUT/org/vekendian/nexus"
    cp -r "$WORK/smali/org/vekendian/nexus/$pkg" "$SMALI_OUT/org/vekendian/nexus/"
done
if [ -f "$WORK/smali/org/vekendian/nexus/Diag.smali" ]; then
    mkdir -p "$SMALI_OUT/org/vekendian/nexus"
    cp "$WORK/smali/org/vekendian/nexus/Diag.smali" "$SMALI_OUT/org/vekendian/nexus/"
else
    rm -f "$SMALI_OUT/org/vekendian/nexus/Diag.smali"
fi
mkdir -p "$(dirname "$DEX_OUT")"
cp "$WORK/dex/classes.dex" "$DEX_OUT"
mkdir -p "$(dirname "$API_JAR")"
cp "$WORK/module-api.jar" "$API_JAR"

echo
echo "smali:     resources/smali/org/vekendian/nexus/{api,modules}"
echo "asset dex: resources/res/raw/ydw_nexus_dexexec"
echo "api jar:   ${API_JAR#$ROOT/}   (classpath for module authors)"