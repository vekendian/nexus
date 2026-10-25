"""The EXTENSIONS tab's bridge into the extension engine.

Everything here is deliberately tiny. The extension system is Java:

    org.vekendian.nexus.extensions.NexusHost      loads the built-in module
        res/raw/ydw_nexus_dexexec  ->  Extension Registry
    JavaExtensionLoader                          loads user's extensions
        files/extensions/<name>.lua  ->  loadstring
        files/extensions/<name>.jar  ->  DexClassLoader + LuaJava

`android/ext/r` therefore keeps four delegates -- pick, boot, render and the
permissions screen -- and
nothing else. The SAF proxy, the preferences file, the document copy, the
classloaders and the card binding all live in Java, where the compiler produces
the register frames and this project has never had to hand-pick them.

What is left to smali, and why:

  * the resource ids, which must stay pinned in nexus_ids.json so the generated
    file is byte-stable across rebuilds -- hence the long const list in render();
  * the entry points that GameGuardian's own lifecycle calls (onPostResume,
    onResume, the power card), which are the only places we are allowed to edit
    inside its code.

The ids reach Java as plain int arguments. That is 19 ids plus the activity,
20 words in one invoke-static/range, which is what keeps render() a single call:
the alternative,
building an int[] in smali, would be forty lines of aput-object for the same
result, and the range form is covered by tests/test_invoke_arity.py like any
other call.

Engine sources: resources/java/{api,host,dexexec}. Generated smali:
resources/smali/org/vekendian/nexus/{api,extensions}. Asset:
resources/res/raw/ydw_nexus_dexexec. Regenerate with `bash build-engine.sh`.
"""

from __future__ import annotations

import os
import re

from .anchors import PatchError

ENGINE = "Lorg/vekendian/nexus/extensions/NexusHost;"
API_PICKER = "org.vekendian.nexus.ModulePicker"

# The ids render() hands the engine, in the order they are loaded into v1..v16.
# This list is the single source of truth for the call's descriptor: the count
# used to be written out by hand and one extra "I" survived, which assembled
# cleanly, passed preflight, and only failed on device with NoSuchMethodError on
# the first draw of the tab. Deriving the descriptor from len() makes that
# impossible, and tests/test_module_engine.py checks the result against the
# generated NexusHost.smali.
RENDER_IDS = (
    "nexus_extensions_list",        # v1  container the cards go into
    "nexus_extensions_empty",       # v2  empty state
    "nexus_extension_card",         # v3  card layout
    "nexus_extension_title",        # v4
    "nexus_extension_meta",         # v5  clean path + size
    "nexus_extension_desc",         # v6  status line
    "nexus_extension_remove",       # v7  remove control
    "nexus_str_extension_jar",      # v8
    "nexus_str_extension_loaded",   # v9
    "nexus_str_extension_idle",     # v10
    "nexus_str_extension_running",  # v11
    "nexus_str_extension_finished", # v12
    "nexus_str_extension_stopped",  # v13
    "nexus_str_extension_error",    # v14
    "nexus_str_extension_remove_title", # v15
    "nexus_str_extension_remove_msg",   # v16
)
RENDER_DESC = "(Landroid/app/Activity;" + "I" * len(RENDER_IDS) + ")V"
# p0 plus v0 (the activity) plus v1..vN for the ids.
RENDER_REGISTERS = 2 + len(RENDER_IDS)

# The four delegates below (extensions pick/drain/render + the permissions screen),
# plus the two power-card hooks smali.py splices into
# nexusPowerOn()/nexusPowerOff().
EXTENSIONS_METHODS = r'''
.method private nexusExtensionsPick()V
    .registers 2

    invoke-static {p0}, @@ENGINE@@->pick(Landroid/app/Activity;)V

    return-void
.end method

.method private nexusExtensionsDrain()V
    .registers 3

    const v0, @@ID:ydw_nexus_dexexec@@

    invoke-static {p0, v0}, @@ENGINE@@->boot(Landroid/app/Activity;I)V

    return-void
.end method

.method private nexusExtensionsRender()V
    .registers 18

    move-object/from16 v0, p0

    const v1, @@ID:nexus_extensions_list@@

    const v2, @@ID:nexus_extensions_empty@@

    const v3, @@ID:nexus_extension_card@@

    const v4, @@ID:nexus_extension_title@@

    const v5, @@ID:nexus_extension_meta@@

    const v6, @@ID:nexus_extension_desc@@

    const v7, @@ID:nexus_extension_remove@@

    const v8, @@ID:nexus_str_extension_jar@@

    const v9, @@ID:nexus_str_extension_loaded@@

    const v10, @@ID:nexus_str_extension_idle@@

    const v11, @@ID:nexus_str_extension_running@@

    const v12, @@ID:nexus_str_extension_finished@@

    const v13, @@ID:nexus_str_extension_stopped@@

    const v14, @@ID:nexus_str_extension_error@@

    const v15, @@ID:nexus_str_extension_remove_title@@

    const v16, @@ID:nexus_str_extension_remove_msg@@

    invoke-static/range {v0 .. @@VHI@@}, @@ENGINE@@->render@@RDESC@@

    return-void
.end method

.method public static nexusPermissionsOpen(Landroid/content/Context;)V
    .registers 5

    const/16 v3, 0xc

    new-array v0, v3, [I

    const/4 v1, 0x0

    const v2, @@ID:nexus_str_perm_title@@

    aput v2, v0, v1

    const/4 v1, 0x1

    const v2, @@ID:nexus_str_perm_allow@@

    aput v2, v0, v1

    const/4 v1, 0x2

    const v2, @@ID:nexus_str_perm_ask@@

    aput v2, v0, v1

    const/4 v1, 0x3

    const v2, @@ID:nexus_str_perm_allow_all@@

    aput v2, v0, v1

    const/4 v1, 0x4

    const v2, @@ID:nexus_str_perm_ask_all@@

    aput v2, v0, v1

    const/4 v1, 0x5

    const v2, @@ID:nexus_str_perm_reset@@

    aput v2, v0, v1

    const/4 v1, 0x6

    const v2, @@ID:nexus_str_perm_reset_done@@

    aput v2, v0, v1

    const/4 v1, 0x7

    const v2, @@ID:nexus_str_perm_close@@

    aput v2, v0, v1

    const/16 v1, 0x8

    const v2, @@ID:nexus_str_perm_install@@

    aput v2, v0, v1

    const/16 v1, 0x9

    const v2, @@ID:nexus_str_perm_uninstall@@

    aput v2, v0, v1

    const/16 v1, 0xa

    const v2, @@ID:nexus_str_perm_list@@

    aput v2, v0, v1

    const/16 v1, 0xb

    const v2, @@ID:nexus_str_perm_import@@

    aput v2, v0, v1

    const/16 v3, 0xc

    invoke-static {p0, v0}, @@ENGINE@@->permissions(Landroid/content/Context;[I)V

    return-void
.end method
'''

# Spliced into nexusPowerOn()/nexusPowerOff(), which are ours: the extension system
# starts and stops extensions with the interface, and nexusPowerApply() already
# dispatches on the nexusPower flag, so these two lines are the whole hook.
POWER_ON_HOOK = """
    invoke-static {}, @@ENGINE@@->powerOn()V
"""

POWER_OFF_HOOK = """
    invoke-static {}, @@ENGINE@@->powerOff()V
"""


STUB_MARKER = "nexus_extensions_disabled"


def extensions_enabled() -> bool:
    """Build-time switch for the extension engine.

    ``NEXUS_EXTENSIONS=0`` emits delegates that return immediately, so
    ``NexusHost.boot()`` is never reached: the Extension Registry asset is never
    extracted, no ``DexClassLoader`` is ever constructed, and ``runAll()`` never
    runs. The asset, the engine classes, the picker activity and every pinned id
    all stay exactly where they are, so the resource table is byte-identical to a
    full build and the only variable is the engine doing its work.

    That is what makes it a bisect rather than a feature flag: a crash that goes
    away with this set cannot be blamed on ids, layouts or the rebrand, only on
    the engine running.
    """
    return os.environ.get("NEXUS_EXTENSIONS", "1") != "0"


def extensions_methods(ids) -> str:
    """The four delegates, with ids and the engine descriptor interpolated."""
    if RENDER_REGISTERS != 18:
        raise PatchError(f"render delegate needs .registers {RENDER_REGISTERS}, "
                         f"not 18 (RENDER_IDS has {len(RENDER_IDS)} entries)")
    out = EXTENSIONS_METHODS.replace("@@ENGINE@@", ENGINE)
    out = out.replace("@@RDESC@@", RENDER_DESC)
    out = out.replace("@@VHI@@", f"v{RENDER_REGISTERS - 2}")
    out = re.sub(r"@@ID:(\w+)@@", lambda m: ids.hex(m.group(1)), out)
    if not extensions_enabled():
        # return-void at the top of each delegate, marker first so it is
        # greppable in the built dex. The .registers line is left alone: smali
        # allocates the frame before executing anything, so a frame that no
        # longer matches the body would be a VerifyError, not a quiet no-op.
        out = re.sub(r"(?m)^(    \.registers \d+)$",
                     r"\1    # " + STUB_MARKER, out)
        out = re.sub(r"(?m)^(    \.registers \d+    # " + STUB_MARKER + r")$",
                     r"\1\n\n    return-void", out)
    return out


def power_hooks(ids) -> tuple:
    """(on, off) fragments for nexusPowerOn()/nexusPowerOff().

    The ids are interpolated even though these carry none, so both fragments
    come from one place and a stale placeholder cannot ship.
    """
    if "@@ID:" in POWER_ON_HOOK or "@@ID:" in POWER_OFF_HOOK:
        raise PatchError("power hooks must not interpolate ids")
    return (POWER_ON_HOOK.replace("@@ENGINE@@", ENGINE),
            POWER_OFF_HOOK.replace("@@ENGINE@@", ENGINE))