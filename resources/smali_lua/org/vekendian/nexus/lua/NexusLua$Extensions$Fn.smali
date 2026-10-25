.class public final Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# One nexus.extensions.<op> function. The class exists so each entry carries its
# own op name ("extensions.list") and script path: invoke() then needs no table
# lookups and no string building, and the permission prompt knows who is
# calling without inspecting the Lua stack.
#
# All flow control lives in NexusLua$Perm.check (allow/ask) and the Java
# bridge (LuaBridge.call). Nothing here decides policy.


.field private final op:Ljava/lang/String;

.field private final script:Ljava/lang/String;


.method public constructor <init>(Ljava/lang/String;Ljava/lang/String;)V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/VarArgFunction;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->op:Ljava/lang/String;

    return-void
.end method


# Call order: engine check first (never prompt for an operation that could not
# run), then the permission gate, then dispatch. Success is luaj's `true`; a
# failure is `nil, message`, so a script reads as
#
#     local ok, err = nexus.extensions.uninstall(path)
#
# and extensions.list() returns a table of records instead of true.
#
# Registers: p0 = this, p1 = call arguments. .locals 3 -> v0 result/scratch,
# v1 op name, v2 script path.


.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 3

    invoke-static {}, Lorg/vekendian/nexus/extensions/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->script:Ljava/lang/String;

    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->op:Ljava/lang/String;

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed

    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :allowed
    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v1, 0x1

    invoke-virtual {p1, v1, v0}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v0

    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->script:Ljava/lang/String;

    iget-object v2, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->op:Ljava/lang/String;

    invoke-static {v1, v2, v0}, Lorg/vekendian/nexus/extensions/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-nez v0, :have

    sget-object v0, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    return-object v0

    :have
    instance-of v1, v0, [Ljava/lang/String;

    if-eqz v1, :failure

    check-cast v0, [Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->table([Ljava/lang/String;)Lluaj/LuaTable;

    move-result-object v0

    return-object v0

    :failure
    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :engine
    const-string v0, "extension system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# nil, message -- the one shape every failure returns.
#
# .locals 3 -> v0 pair, v1 index, v2 value.


.method private static error(Ljava/lang/String;)Lluaj/Varargs;
    .locals 3

    const/4 v0, 0x2

    new-array v0, v0, [Lluaj/LuaValue;

    const/4 v1, 0x0

    sget-object v2, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    aput-object v2, v0, v1

    const/4 v1, 0x1

    invoke-static {p0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v2

    aput-object v2, v0, v1

    invoke-static {v0}, Lluaj/LuaValue;->O2([Lluaj/LuaValue;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# String[] records ("path\tname\tstate\tversion\tautostart", no trailing
# fields, tabs/newlines already sanitized on the Java side) -> Lua table of
# tables. Lua arrays are 1-based, so the record at index 0 becomes t[1].
#
# .locals 8 -> v0 out table, v1 tab, v2 source index, v3 fields of one
# record, v4 record table, v5 key, v6 index/scratch, v7 value.


.method private static table([Ljava/lang/String;)Lluaj/LuaTable;
    .locals 8

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    const-string v1, "\t"

    const/4 v2, 0x0

    :loop
    array-length v3, p0

    if-ge v2, v3, :done

    aget-object v3, p0, v2

    invoke-virtual {v3, v1}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v3

    new-instance v4, Lluaj/LuaTable;

    invoke-direct {v4}, Lluaj/LuaTable;-><init>()V

    const-string v5, "path"

    const/4 v6, 0x0

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "name"

    const/4 v6, 0x1

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "state"

    const/4 v6, 0x2

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "version"

    const/4 v6, 0x3

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "autostart"

    const/4 v6, 0x4

    aget-object v6, v3, v6

    const-string v7, "true"

    invoke-virtual {v6, v7}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v6

    if-eqz v6, :not_true

    sget-object v6, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    goto :put

    :not_true
    sget-object v6, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    :put
    invoke-virtual {v4, v5, v6}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    add-int/lit8 v5, v2, 0x1

    invoke-virtual {v0, v5, v4}, Lluaj/LuaValue;->Y1(ILluaj/LuaValue;)V

    add-int/lit8 v2, v2, 0x1

    goto :loop

    :done
    return-object v0
.end method
