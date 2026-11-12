.class public final Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# One nexus.modules.<op> function. The class exists so each entry carries its
# own op name ("modules.list") and script path: invoke() then needs no table
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

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->op:Ljava/lang/String;

    return-void
.end method


# Call order: engine check first (never prompt for an operation that could not
# run), then the permission gate, then dispatch. Success is luaj's `true`; a
# failure is `nil, message`, so a script reads as
#
#     local ok, err = nexus.modules.uninstall(path)
#
# and modules.list() returns a table of records instead of true.
#
# install() has three shapes: install(path), install(path, {metadata}) and
# install({content=..., metadata}). The table shapes are detected here because
# a Lua string and a Lua table both arrive as LuaValue; the byte copy itself
# lives in tableInstall/contentBytes, since only smali may touch luaj's
# LuaString internals.
#
# Registers: p0 = this, p1 = call arguments. .locals 5 -> v0 arg/result,
# v1..v2 op/scratch, v3..v4 scratch.


.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 5

    invoke-static {}, Lorg/vekendian/nexus/modules/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->script:Ljava/lang/String;

    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->op:Ljava/lang/String;

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed

    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :allowed
    # arg[1] may be absent (list() takes no path). Read it as a LuaValue so a
    # table can be told apart from a string; absent becomes an empty string.
    invoke-virtual {p1}, Lluaj/Varargs;->U()I

    move-result v0

    if-lez v0, :fn_no_arg

    sget-object v1, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v2, 0x1

    invoke-virtual {p1, v2, v1}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    goto :fn_have_arg

    :fn_no_arg
    const-string v0, ""

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    :fn_have_arg
    # Only install() takes a table. Every other op keeps the old path: the
    # argument is a string and LuaBridge.call handles it.
    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->op:Ljava/lang/String;

    const-string v2, "modules.install"

    invoke-virtual {v1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :fn_plain_call

    instance-of v1, v0, Lluaj/LuaTable;

    if-eqz v1, :fn_check_second

    # install({content=..., ...})
    check-cast v0, Lluaj/LuaTable;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->tableInstall(Lluaj/LuaTable;Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :fn_check_second
    # install(path, {metadata}): the second argument is the table.
    invoke-virtual {p1}, Lluaj/Varargs;->U()I

    move-result v1

    const/4 v2, 0x2

    if-lt v1, v2, :fn_plain_call

    sget-object v1, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v2, 0x2

    invoke-virtual {p1, v2, v1}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v1

    instance-of v2, v1, Lluaj/LuaTable;

    if-eqz v2, :fn_plain_call

    check-cast v1, Lluaj/LuaTable;

    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v2

    invoke-static {v1, v2}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->tableInstall(Lluaj/LuaTable;Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :fn_plain_call
    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v0

    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->script:Ljava/lang/String;

    iget-object v2, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->op:Ljava/lang/String;

    invoke-static {v1, v2, v0}, Lorg/vekendian/nexus/modules/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->result(Ljava/lang/Object;)Lluaj/Varargs;

    move-result-object v0

    return-object v0

    :engine
    const-string v0, "module system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# Object -> the Lua value a caller sees: null is `true`, String[] is a table
# of records, anything else is `nil, message`.
#
# .locals 3 -> v0 pair/table/scratch.


.method private static result(Ljava/lang/Object;)Lluaj/Varargs;
    .locals 3

    if-nez p0, :have

    sget-object v0, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    return-object v0

    :have
    instance-of v0, p0, [Ljava/lang/String;

    if-eqz v0, :failure

    check-cast p0, [Ljava/lang/String;

    invoke-static {p0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->table([Ljava/lang/String;)Lluaj/LuaTable;

    move-result-object v0

    return-object v0

    :failure
    check-cast p0, Ljava/lang/String;

    invoke-static {p0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# One string field of the install table, or null when the key is absent.
#
# .locals 3 -> v0 result, v1 value, v2 scratch.


.method private static stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;
    .locals 3

    const/4 v0, 0x0

    invoke-static {p1}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v1

    invoke-virtual {p0, v1}, Lluaj/LuaValue;->U0(Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v1

    invoke-virtual {v1}, Lluaj/LuaValue;->l1()Z

    move-result v2

    if-eqz v2, :nil

    invoke-virtual {v1}, Lluaj/LuaValue;->g0()Ljava/lang/String;

    move-result-object v0

    :nil
    return-object v0
.end method


# The `content` field as raw bytes, or null when the key is absent. A Lua
# string is a byte slice (P[Q..Q+R)), so copyOfRange is the only safe way to
# hand the host Java a byte[] without referencing luaj there.
#
# .locals 5 -> v0 value/bytes, v1 array, v2 offset, v3 length, v4 end.


.method private static contentBytes(Lluaj/LuaTable;)[B
    .locals 5

    const-string v0, "content"

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    invoke-virtual {p0, v0}, Lluaj/LuaValue;->U0(Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    instance-of v1, v0, Lluaj/LuaString;

    if-eqz v1, :none

    check-cast v0, Lluaj/LuaString;

    iget-object v1, v0, Lluaj/LuaString;->P:[B

    iget v2, v0, Lluaj/LuaString;->Q:I

    iget v3, v0, Lluaj/LuaString;->R:I

    add-int v4, v2, v3

    invoke-static {v1, v2, v4}, Ljava/util/Arrays;->copyOfRange([BII)[B

    move-result-object v0

    return-object v0

    :none
    const/4 v0, 0x0

    return-object v0
.end method


# One install from a table: content when present, otherwise path. The explicit
# path from a two-argument install wins over the table's own "path" key.
#
# .locals 8 -> v0 content, v1 path, v2 name, v3 description, v4 version,
# v5 type, v6 result.


.method private static tableInstall(Lluaj/LuaTable;Ljava/lang/String;)Lluaj/Varargs;
    .locals 8

    invoke-static {p0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->contentBytes(Lluaj/LuaTable;)[B

    move-result-object v0

    const-string v1, "path"

    invoke-static {p0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    if-eqz p1, :have_path

    move-object v1, p1

    :have_path
    const-string v2, "name"

    invoke-static {p0, v2}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    const-string v3, "description"

    invoke-static {p0, v3}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    const-string v4, "version"

    invoke-static {p0, v4}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    const-string v5, "type"

    invoke-static {p0, v5}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->stringField(Lluaj/LuaTable;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    if-eqz v0, :path_install

    invoke-static {v0, v2, v3, v4, v5}, Lorg/vekendian/nexus/modules/LuaBridge;->installBytes([BLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v6

    goto :done

    :path_install
    if-eqz v1, :no_path

    invoke-static {v1, v2, v3, v4, v5}, Lorg/vekendian/nexus/modules/LuaBridge;->installPath(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v6

    goto :done

    :no_path
    const-string v6, "missing module path"

    invoke-static {v6}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v6

    return-object v6

    :done
    invoke-static {v6}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Fn;->result(Ljava/lang/Object;)Lluaj/Varargs;

    move-result-object v6

    return-object v6
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


# String[] records ("path\tname\tid\tstate\tversion\tautostart\ttype\tdescription\tmessage", no trailing fields, tabs/newlines already sanitized on the Java side) -> Lua table of tables. Lua arrays are 1-based, so the record at index 0 becomes t[1].
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

    # split with limit -1: Java drops trailing empty fields by default, so a
    # module with no description/message would split to 7 elements and the
    # description/message reads below would run off the end.
    const/4 v6, -0x1

    invoke-virtual {v3, v1, v6}, Ljava/lang/String;->split(Ljava/lang/String;I)[Ljava/lang/String;

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

    const-string v5, "id"

    const/4 v6, 0x2

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "state"

    const/4 v6, 0x3

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "version"

    const/4 v6, 0x4

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "autostart"

    const/4 v6, 0x5

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

    const-string v5, "type"

    const/4 v6, 0x6

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "description"

    const/4 v6, 0x7

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v5, "message"

    const/16 v6, 0x8

    aget-object v7, v3, v6

    invoke-static {v7}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v7

    invoke-virtual {v4, v5, v7}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    add-int/lit8 v5, v2, 0x1

    invoke-virtual {v0, v5, v4}, Lluaj/LuaValue;->Y1(ILluaj/LuaValue;)V

    add-int/lit8 v2, v2, 0x1

    goto :loop

    :done
    return-object v0
.end method
