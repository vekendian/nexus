.class public final Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# The nexus.modules.import(name) builder.
#
# One call, three module types:
#
#   JAR/DEX -- bridge "modules.spec" returns the @Export records; each one
#              becomes a NexusLua$Modules$Jfn (script, id, name/pspec/ret)
#              under its method name, and the record table comes back as the
#              module value. Every method the jar's own imports and classes
#              need resolves through this script's calling environment.
#   LUA     -- spec comes back empty, so the builder bridges "modules.source"
#              and loadstrings the code in the caller's own Globals (O3, the
#              same entry GameGuardian's loader uses for .lua files). The
#              chunk's return value -- conventionally the module table -- is
#              what import() returns, so `local zip = nexus.modules.import
#              ("zip")` binds the table the module returned.
#
# The probe is ordered spec-then-source and both are gated by one capability,
# "modules.import": one prompt row covers import, spec lookups, calls into
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

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->env:Lluaj/LuaValue;

    return-void
.end method


.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 14

    invoke-static {}, Lorg/vekendian/nexus/modules/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine


    # id = tostring(args[1]); a missing argument stringifies to "nil" and
    # fails the lookup with the usual "no module at ..." message.

    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v1, 0x1

    invoke-virtual {p1, v1, v0}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v10


    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    const-string v1, "modules.import"

    invoke-static {v0, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed


    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :allowed
    # Probe one: exported methods of a JAR/DEX. A String result is an error;

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    const-string v1, "modules.spec"

    invoke-static {v0, v1, v10}, Lorg/vekendian/nexus/modules/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-eqz v0, :source

    instance-of v1, v0, Ljava/lang/String;

    if-eqz v1, :spec_array

    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :spec_array
    check-cast v0, [Ljava/lang/String;

    move-object v12, v0

    array-length v1, v12

    if-lez v1, :class_only


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

    new-instance v8, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;

    iget-object v9, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    invoke-direct {v8, v9, v10, v11}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;-><init>(Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;)V

    invoke-virtual {v13, v5, v8}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V


    :jar_next
    add-int/lit8 v2, v2, 0x1

    goto :jar_loop


    :jar_done
    # Register before returning: the table can hand out a class the moment the
    # script holds it.
    invoke-direct {p0, v10}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->registerLoader(Ljava/lang/String;)Z

    # Exports stay real keys; the metatable only answers for the rest, so an
    # @Export named like a class still wins.
    invoke-static {v10}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->classTable(Ljava/lang/String;)Lluaj/LuaTable;

    move-result-object v0

    invoke-virtual {v13, v0}, Lluaj/LuaTable;->k2(Lluaj/LuaValue;)Lluaj/LuaValue;

    return-object v13


    :class_only
    # No @Export records. A jar/dex that only carries classes still imports --
    # as a table whose __index resolves them -- but a .lua has no loader, so
    # registerLoader answers false and the source probe takes over.

    invoke-direct {p0, v10}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->registerLoader(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :source

    invoke-static {v10}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->classTable(Ljava/lang/String;)Lluaj/LuaTable;

    move-result-object v0

    return-object v0


    :source
    # Probe two: source code of a Lua module. The envelope is {"r", source}

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    const-string v1, "modules.source"

    invoke-static {v0, v1, v10}, Lorg/vekendian/nexus/modules/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-eqz v0, :nothing

    instance-of v1, v0, Ljava/lang/String;

    if-eqz v1, :src_array

    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

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

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

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

    const-string v9, "nexus.modules.import:"

    invoke-virtual {v8, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    iget-object v11, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->env:Lluaj/LuaValue;

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

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

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

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :engine
    const-string v0, "module system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# Registers the module's ClassLoader with luaj so its classes resolve, and
# answers whether there was one. Called from both jar paths -- with exports and
# without -- because either kind of module can carry classes worth reaching.
#
# The bridge returns the loader, null for a .lua module, or an error string;
# only a ClassLoader is registered, so a failure here degrades to the old
# "nothing importable" message instead of surfacing as a second error.
#
# An instance method, not static, so the script name comes from p0 rather than
# from a call site's register -- with .locals 14 the p-registers are v14/v15 and
# a 35c invoke cannot name anything above v15.
#
# It stays private, and every call site uses invoke-direct: ART rejects the
# whole class when invoke-virtual names a private method
# (VERIFY_ERROR_BAD_CLASS_HARD, "invoke-super/virtual can't be used on private
# method"), and that VerifyError would surface at new-instance inside
# Modules.install -- silently, because Script.nexusInstall catches
# Throwables -- as a nil nexus.modules beside a working nexus.version.
#
# v0 loader/result, v1 instanceof test.

.method private registerLoader(Ljava/lang/String;)Z
    .locals 2

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Import;->script:Ljava/lang/String;

    const-string v1, "modules.loader"

    invoke-static {v0, v1, p1}, Lorg/vekendian/nexus/modules/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    instance-of v1, v0, Ljava/lang/ClassLoader;

    if-eqz v1, :none

    check-cast v0, Ljava/lang/ClassLoader;

    invoke-static {v0}, Lluaj/Hlp;->registerDex(Ljava/lang/ClassLoader;)V

    const/4 v0, 0x1

    return v0


    :none
    const/4 v0, 0x0

    return v0
.end method


# The value nexus.modules.import() hands back for a jar/dex: an empty table
# whose __index turns an absent key into a class from that module. Built for
# both paths -- with exports (attached to the Jfn table) and without (returned
# on its own) -- so `mod.SomeClass` behaves the same either way.
#
# v0 table, v1 metatable, v2 __index function, v3 "__index".

.method private static classTable(Ljava/lang/String;)Lluaj/LuaTable;
    .locals 4

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    new-instance v1, Lluaj/LuaTable;

    invoke-direct {v1}, Lluaj/LuaTable;-><init>()V

    new-instance v2, Lorg/vekendian/nexus/lua/NexusLua$Modules$Cls;

    invoke-direct {v2, p0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Cls;-><init>(Ljava/lang/String;)V

    const-string v3, "__index"

    invoke-virtual {v1, v3, v2}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    invoke-virtual {v0, v1}, Lluaj/LuaTable;->k2(Lluaj/LuaValue;)Lluaj/LuaValue;

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
