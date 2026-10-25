.class public final Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# The nexus.extensions.import(name) builder.
#
# One call, three extension types:
#
#   JAR/DEX -- bridge "extensions.spec" returns the @Export records; each one
#              becomes a NexusLua$Extensions$Jfn (script, id, name/pspec/ret)
#              under its method name, and the record table comes back as the
#              module value. Every method the jar's own imports and classes
#              need resolves through this script's calling environment.
#   LUA     -- spec comes back empty, so the builder bridges "extensions.source"
#              and loadstrings the code in the caller's own Globals (O3, the
#              same entry GameGuardian's loader uses for .lua files). The
#              chunk's return value -- conventionally the module table -- is
#              what import() returns, so `local zip = nexus.extensions.import
#              ("zip")` binds the table the extension returned.
#
# The probe is ordered spec-then-source and both are gated by one capability,
# "extensions.import": one prompt row covers import, spec lookups, calls into
# imported methods and source reads alike. The id matches the bare file name
# ("zip"), not the full path install() takes.
#
# p1 of install() is the script's Globals (NexusLua.install receives the
# environment GameGuardian hands to nexusInstall; a Globals is a LuaValue), so
# the constructor stores it as LuaValue and check-casts at the one place it is
# used. A wrong cast -- never seen in practice -- degrades to an error string
# through the same catch that guards the load, never to a crash.
#
# Registers in invoke(): v0 bridge object, v1 int/bool, v2 loop index, v3
# unused, v4 index/mode const, v5 record/key/scratch, v6 separator const,
# v7 stream, v8 Jfn instance/StringBuilder, v9 script-iget/chunkname, v10 id
# (persists), v11 fields array/env Globals, v12 records array/chunk (persists
# inside its path), v13 result table.
#
# Registers in the jar loop are arranged so invoke-direct {v8, v9, v10, v11}
# is contiguous: instance, script, id, fields -- the four operands Jfn's
# constructor takes.


.field private final script:Ljava/lang/String;

.field final env:Lluaj/LuaValue;


.method public constructor <init>(Ljava/lang/String;Lluaj/LuaValue;)V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/VarArgFunction;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->env:Lluaj/LuaValue;

    return-void
.end method


.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 14

    invoke-static {}, Lorg/vekendian/nexus/extensions/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine


    # id = tostring(args[1]); a missing argument stringifies to "nil" and
    # fails the lookup with the usual "no extension at ..." message.

    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v1, 0x1

    invoke-virtual {p1, v1, v0}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v10


    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->script:Ljava/lang/String;

    const-string v1, "extensions.import"

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed


    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :allowed
    # Probe one: exported methods of a JAR/DEX. A String result is an error;

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->script:Ljava/lang/String;

    const-string v1, "extensions.spec"

    invoke-static {v0, v1, v10}, Lorg/vekendian/nexus/extensions/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-eqz v0, :source

    instance-of v1, v0, Ljava/lang/String;

    if-eqz v1, :spec_array

    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :spec_array
    check-cast v0, [Ljava/lang/String;

    move-object v12, v0

    array-length v1, v12

    if-lez v1, :source


    new-instance v13, Lluaj/LuaTable;

    invoke-direct {v13}, Lluaj/LuaTable;-><init>()V

    const/4 v2, 0x0


    :jar_loop
    array-length v1, v12

    if-ge v2, v1, :jar_done


    aget-object v5, v12, v2

    const-string v6, "\t"

    invoke-virtual {v5, v6}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v11

    array-length v1, v11

    const/4 v4, 0x3

    if-lt v1, v4, :jar_next


    const/4 v4, 0x0

    aget-object v5, v11, v4

    new-instance v8, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Jfn;

    iget-object v9, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->script:Ljava/lang/String;

    invoke-direct {v8, v9, v10, v11}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Jfn;-><init>(Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;)V

    invoke-virtual {v13, v5, v8}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V


    :jar_next
    add-int/lit8 v2, v2, 0x1

    goto :jar_loop


    :jar_done
    return-object v13


    :source
    # Probe two: source code of a Lua extension. The envelope is {"r", source}

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->script:Ljava/lang/String;

    const-string v1, "extensions.source"

    invoke-static {v0, v1, v10}, Lorg/vekendian/nexus/extensions/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-eqz v0, :nothing

    instance-of v1, v0, Ljava/lang/String;

    if-eqz v1, :src_array

    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :src_array
    check-cast v0, [Ljava/lang/String;

    move-object v12, v0

    array-length v1, v12

    const/4 v4, 0x2

    if-ne v1, v4, :nothing


    const/4 v4, 0x0

    aget-object v5, v12, v4

    const-string v6, "r"

    invoke-virtual {v5, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :src_ok

    const-string v6, "e"

    invoke-virtual {v5, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :nothing

    const/4 v4, 0x1

    aget-object v0, v12, v4

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :src_ok
    const/4 v4, 0x1

    aget-object v5, v12, v4


    :try_load
    invoke-virtual {v5}, Ljava/lang/String;->getBytes()[B

    move-result-object v6

    new-instance v7, Ljava/io/ByteArrayInputStream;

    invoke-direct {v7, v6}, Ljava/io/ByteArrayInputStream;-><init>([B)V

    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8}, Ljava/lang/StringBuilder;-><init>()V

    const-string v9, "nexus.extensions.import:"

    invoke-virtual {v8, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    iget-object v11, p0, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->env:Lluaj/LuaValue;

    check-cast v11, Lluaj/Globals;

    const-string v4, "t"

    invoke-virtual {v11, v7, v9, v4, v11}, Lluaj/Globals;->O3(Ljava/io/InputStream;Ljava/lang/String;Ljava/lang/String;Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v12

    invoke-virtual {v12}, Lluaj/LuaValue;->call()Lluaj/LuaValue;

    move-result-object v12

    :try_load_end
    return-object v12

    .catch Ljava/lang/Throwable; {:try_load .. :try_load_end} :load_err


    :load_err
    move-exception v5

    invoke-virtual {v5}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :nothing
    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "nothing importable at "

    invoke-virtual {v7, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v7, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v7}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :engine
    const-string v0, "extension system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Extensions$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# nil, message -- the one shape every failure returns.
#
# v0 pair, v1 index, v2 value.

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
