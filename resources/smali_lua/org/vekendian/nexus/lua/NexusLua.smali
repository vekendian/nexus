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
# The table itself never depends on the extension engine: `nexus` and
# `nexus.version` exist in every script, even one that runs before Nexus has
# booted. Only categories that need the engine (NexusLua$Extensions) check for
# it, and only they return "extension system is not running".
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

    invoke-static {v2}, Lluaj/LuaValue;->valueOf(Ljava/lang/String;)Lluaj/LuaValue;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    invoke-static {p0, v0, p1}, Lorg/vekendian/nexus/lua/NexusLua$Extensions;->install(Ljava/lang/String;Lluaj/LuaValue;Lluaj/LuaValue;)V

    const-string v1, "nexus"

    invoke-virtual {p1, v1, v0}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    :done
    return-void
.end method
