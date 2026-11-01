.class public final Lorg/vekendian/nexus/lua/NexusLua$Modules;
.super Ljava/lang/Object;
.source "NexusLua.java"


# The `modules` category: builds nexus.modules and registers one function
# object per operation.
#
# The operation names are themselves the permission capabilities
# ("modules.install", ...), so the prompt, the remembered choices and the
# dispatch table can never disagree about what was asked for.
#
# import() is the exception in one way: its capability is "modules.import"
# for the builder and every function object it hands out, because importing,
# inspecting and calling one module are one action. It needs the caller's
# Globals to loadstring Lua modules in, which is why the environment rides
# along as the third parameter.
#
# Registers: p0 = script path, p1 = the nexus table, p2 = the script
# environment (a Globals held as LuaValue). .locals 4 -> v0 modules table,
# v1 key, v2 function object, v3 op name.


.method public static install(Ljava/lang/String;Lluaj/LuaValue;Lluaj/LuaValue;)V
    .locals 4

    if-eqz p1, :done

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    const-string v1, "install"

    new-instance v2, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;

    const-string v3, "modules.install"

    invoke-direct {v2, p0, v3}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v1, "uninstall"

    new-instance v2, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;

    const-string v3, "modules.uninstall"

    invoke-direct {v2, p0, v3}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v1, "list"

    new-instance v2, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;

    const-string v3, "modules.list"

    invoke-direct {v2, p0, v3}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v1, "import"

    new-instance v2, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;

    invoke-direct {v2, p0, p2}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;-><init>(Ljava/lang/String;Lluaj/LuaValue;)V

    invoke-virtual {v0, v1, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v1, "modules"

    invoke-virtual {p1, v1, v0}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    :done
    return-void
.end method
