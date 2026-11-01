.class public final Lorg/vekendian/nexus/lua/NexusLua;
.super Ljava/lang/Object;
.source "NexusLua.java"


# The Lua-visible `nexus` table.
#
# Built once per script by android.ext.Script, right after it registers `gg`
# (see the nexusInstall() helper this patcher appends there). Touching Script is
# the one GG-owned edit the namespace needs, and it is one call line plus one
# helper method.
#
# The table itself never depends on the module engine: `nexus` and
# `nexus.version` exist in every script, even one that runs before Nexus has
# booted. Only categories that need the engine (NexusLua$Modules) check for
# it, and only they return "module system is not running".
#
# Categories are registered here, one call per category. Adding one is a new
# NexusLua$<Category> class and one line, without touching this table code or
# the permission gate.
#
# Registers: p0 = script path (File#toString or String, may be null),
# p1 = the script environment. .locals 4 -> v0 nexus table, v1 key,
# v2 the version string.


.method public static install(Ljava/lang/String;Lluaj/LuaValue;)V
    .locals 4

    if-eqz p1, :done

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    const-string v1, "version"

    const-string v2, "1.0.0"

    # K2(String) is this build's obfuscated LuaValue.valueOf(String) -> LuaString.
    # LuaValue has no method named valueOf at all: a plain name here silently
    # killed the whole install (caught in Script.nexusInstall), leaving nexus
    # nil in every script. Pinned by the stock-resolution test in
    # test_lua_bridge.py.
    invoke-static {v2}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    # The global is bound BEFORE the categories attach. The Script-side helper
    # runs this under a silentThrowable catch; if a category could abort the
    # install, the script's view of nexus would be a whole-table nil, and even
    # nexus.version would be unreadable. Failures now shrink the table's
    # contents at worst: a nil nexus.modules, never a nil nexus.
    const-string v1, "nexus"

    invoke-virtual {p1, v1, v0}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    invoke-static {p0, v0, p1}, Lorg/vekendian/nexus/lua/NexusLua$Modules;->install(Ljava/lang/String;Lluaj/LuaValue;Lluaj/LuaValue;)V

    :done
    return-void
.end method
