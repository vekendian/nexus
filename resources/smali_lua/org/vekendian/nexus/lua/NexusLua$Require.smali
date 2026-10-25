.class public final Lorg/vekendian/nexus/lua/NexusLua$Require;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"

# nexus.require(name) -- convenience wrapper around nexus.extensions.import(name).
# Scripts can write `local zip = nexus.require("zip")` instead of the longer form.
# Same spec/source probe, same loadstring path, same Jfn table for JAR/DEX.

.field private final script:Ljava/lang/String;

.field final env:Lluaj/LuaValue;

.method public constructor <init>(Ljava/lang/String;Lluaj/LuaValue;)V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/VarArgFunction;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Require;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Require;->env:Lluaj/LuaValue;

    return-void
.end method

.method public invoke(Lluaj/Varargs;)Lluang/Varargs;
    .locals 5

    invoke-static {}, Lorg/vekendian/nexus/extensions/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Require;->script:Ljava/lang/String;

    const-string v1, "extensions.import"

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed

    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Require;->error(Ljava/lang/String;)Lluang/Varargs;

    move-result-object v0

    return-object v0

:allowed
    # Delegate to Import with the same varargs (args[1] = name).
    new-instance v3, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;

    iget-object v4, p0, Lorg/vekendian/nexus/lua/NexusLua$Require;->script:Ljava/lang/String;

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Require;->env:Lluang/LuaValue;

    invoke-direct {v3, v4, v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;-><init>(Ljava/lang/String;Lluang/LuaValue;)V

    invoke-virtual {v3, p1}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->invoke(Lluang/Varargs;)Lluang/Varargs;

    move-result-object v0

    return-object v0

:engine
    const-string v0, "extension system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Require;->error(Ljava/lang/String;)Lluang/Varargs;

    move-result-object v0

    return-object v0

.end method

.method private static error(Ljava/lang/String;)Lluang/Varargs;
    .locals 3

    const/4 v0, 0x2

    new-array v0, v0, [Lluang/LuaValue;

    const/4 v1, 0x0

    sget-object v2, Lluang/LuaValue;->c:Lluang/LuaValue;

    aput-object v2, v0, v1

    const/4 v1, 0x1

    invoke-static {p0}, Lluang/LuaValue;->K2(Ljava/lang/String;)Lluang/LuaString;

    move-result-object v2

    aput-object v2, v0, v1

    invoke-static {v0}, Lluang/LuaValue;->O2([Lluang/LuaValue;)Lluang/Varargs;

    move-result-object v0

    return-object v0

.end method
