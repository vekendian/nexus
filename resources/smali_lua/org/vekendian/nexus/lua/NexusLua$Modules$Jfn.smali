.class public final Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# One exported method of an imported jar/dex module -- the function object
# nexus.modules.import() builds per @Export record and puts in the table it
# returns. Carries every fact the call will need: script (permission label),
# jar (module id), method (export name), pspec (parameter type codes) and
# ret (return type code). invoke() needs no table lookups and no parser: read
# the arguments, escape-join one packed record, dispatch, re-type the envelope.
#
# The wire contract (documented next to Export.java and the engine's
# invokeJarMethod):
#   packed record: jar <tab> method <tab> pspec <tab> args -- tab separators
#   escaping inside args only: backslash -> \\, tab -> \t, newline -> \n
#   nil arguments marshal as an empty slot, preserving positions
#   envelope from the engine: {"r", value}, or {"e", reason} on failure
#   retype by ret: v -> true, s -> string, n -> number, b -> boolean
#
# All policy lives in NexusLua$Perm.check and LuaBridge: nothing here decides
# what is allowed. The capability is "modules.import" for every call this
# class can make, so the prompt names the action once and remembers it once.


.field private final script:Ljava/lang/String;

.field private final jar:Ljava/lang/String;

.field private final method:Ljava/lang/String;

.field private final pspec:Ljava/lang/String;

.field private final ret:Ljava/lang/String;


.method public constructor <init>(Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;)V
    .locals 5
    # p0 = this, p1 = script, p2 = jar id, p3 = method/pspec/ret fields.
    # A malformed record collapses to an empty export, which never matches --
    # the engine rejects the call and the user sees the reason.

    invoke-direct {p0}, Lluaj/lib/VarArgFunction;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->jar:Ljava/lang/String;

    const-string v0, ""

    const-string v1, ""

    const-string v2, ""

    array-length v3, p3

    const/4 v4, 0x3

    if-lt v3, v4, :short

    const/4 v3, 0x0

    aget-object v0, p3, v3

    const/4 v3, 0x1

    aget-object v1, p3, v3

    const/4 v3, 0x2

    aget-object v2, p3, v3

    :short
    iput-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->method:Ljava/lang/String;

    iput-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->pspec:Ljava/lang/String;

    iput-object v2, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->ret:Ljava/lang/String;

    return-void
.end method


# Invoke: pack and dispatch, then re-type the engine's envelope.
#
# Registers: p0 = this, p1 = arguments. v0 bridge object (and later the
# envelope's value string), v1 int, v2 loop index, v3 arg LuaValue, v4
# StringBuilder, v5 char/message scratch, v6 scratch string, v7 tab const,
# v8/v9 the J2(D) wide pair, v10 packed record, v11 unused, v12 envelope
# array, v13 ret string holder.

.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 14


    invoke-static {}, Lorg/vekendian/nexus/modules/LuaBridge;->ready()Z

    move-result v0

    if-eqz v0, :engine

    iget-object v4, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->script:Ljava/lang/String;

    const-string v1, "modules.import"

    invoke-static {v4, v1}, Lorg/vekendian/nexus/lua/NexusLua$Perm;->check(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :allowed


    const-string v0, "permission denied"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :allowed
    invoke-virtual {p1}, Lluaj/Varargs;->U()I

    move-result v1


    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V


    iget-object v5, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->jar:Ljava/lang/String;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v5, 0x9

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;


    iget-object v5, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->method:Ljava/lang/String;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;


    const/16 v5, 0x9

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;


    iget-object v5, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->pspec:Ljava/lang/String;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;


    const/16 v5, 0x9

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;


    const/4 v2, 0x1

    const/16 v7, 0x9


    :arg_loop
    if-gt v2, v1, :arg_done

    const/4 v6, 0x1

    if-eq v2, v6, :arg_first

    invoke-virtual {v4, v7}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;


    :arg_first
    sget-object v6, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    invoke-virtual {p1, v2, v6}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v3


    sget-object v6, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    if-eq v3, v6, :arg_next


    invoke-virtual {v3}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->escape(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;


    :arg_next

    add-int/lit8 v2, v2, 0x1

    goto :arg_loop


    :arg_done
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10


    iget-object v4, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->script:Ljava/lang/String;

    const-string v5, "modules.invoke"

    invoke-static {v4, v5, v10}, Lorg/vekendian/nexus/modules/LuaBridge;->call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    if-eqz v0, :success


    instance-of v1, v0, [Ljava/lang/String;

    if-eqz v1, :failure


    check-cast v0, [Ljava/lang/String;

    move-object v12, v0

    array-length v1, v12

    const/4 v2, 0x2

    if-ne v1, v2, :bad_envelope


    const/4 v2, 0x0

    aget-object v6, v12, v2

    const-string v7, "e"

    invoke-virtual {v6, v7}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    # if-nez branches on ZERO, so `if-nez v1, :envelope_error` here did the
    # opposite of what the tag says: an {"e", msg} envelope (v1 != 0) fell
    # through to the "r" test and reported "malformed result from module",
    # while a {"r", value} envelope (v1 == 0) branched straight into the error
    # handler and returned its value as an error. Only "e" is an error; every
    # other tag has to reach the "r" test below.
    if-eqz v1, :tag_r

    goto :envelope_error


    :tag_r
    const-string v7, "r"

    invoke-virtual {v6, v7}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :bad_envelope


    const/4 v2, 0x1

    aget-object v0, v12, v2

    iget-object v13, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->ret:Ljava/lang/String;

    const/4 v7, 0x0

    invoke-virtual {v13, v7}, Ljava/lang/String;->charAt(I)C

    move-result v13


    const/16 v7, 0x76

    if-eq v13, v7, :ret_v

    const/16 v7, 0x73

    if-eq v13, v7, :ret_s

    const/16 v7, 0x6e

    if-eq v13, v7, :ret_n

    const/16 v7, 0x62

    # anything unrecognised rides the string treatment; only 'b' itself goes
    # to the boolean branch below.
    if-ne v13, v7, :ret_s


    :ret_b
    const-string v6, "true"

    invoke-virtual {v0, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :b_false


    :ret_v
    sget-object v0, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    return-object v0


    :b_false
    sget-object v0, Lluaj/LuaValue;->e:Lluaj/LuaBoolean;

    return-object v0


    :ret_s
    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    return-object v0


    :ret_n
    :try_n
    invoke-static {v0}, Ljava/lang/Double;->parseDouble(Ljava/lang/String;)D

    move-result-wide v8


    invoke-static {v8, v9}, Lluaj/LuaDouble;->J2(D)Lluaj/LuaNumber;

    move-result-object v0

    return-object v0
    :try_n_end
    .catch Ljava/lang/NumberFormatException; {:try_n .. :try_n_end} :n_bad


    :n_bad
    move-exception v5

    const-string v6, "not a number returned by module: "

    invoke-virtual {v5}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v6, v5}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :envelope_error
    const/4 v2, 0x1

    aget-object v0, v12, v2

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :bad_envelope
    const-string v0, "malformed result from module"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :failure
    check-cast v0, Ljava/lang/String;

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0


    :success
    sget-object v0, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    return-object v0


    :engine
    const-string v0, "module system is not running"

    invoke-static {v0}, Lorg/vekendian/nexus/lua/NexusLua$Modules$Jfn;->error(Ljava/lang/String;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method


# Backslash escaping for one argument: backslash doubles, tab and newline
# become their two-character forms. The engine's unpackArgs reverses exactly
# this, so the escape set cannot grow without changing both sides.
#
# v0 in, v1 out, v2 index, v3 char, v4 length, v5 scratch.

.method private static escape(Ljava/lang/String;)Ljava/lang/String;
    .locals 6


    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V


    const/4 v2, 0x0


    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v4


    :esc_loop
    if-ge v2, v4, :esc_done


    invoke-virtual {v0, v2}, Ljava/lang/String;->charAt(I)C

    move-result v3


    const/16 v5, 0x5c

    if-eq v3, v5, :esc_backslash


    const/16 v5, 0x9

    if-eq v3, v5, :esc_tab


    const/16 v5, 0xa

    if-eq v3, v5, :esc_newline


    :esc_plain
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    goto :esc_step


    :esc_backslash
    const-string v5, "\\\\"

    goto :esc_write


    :esc_tab
    const-string v5, "\\t"

    goto :esc_write


    :esc_newline
    const-string v5, "\\n"


    :esc_write
    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;


    :esc_step
    add-int/lit8 v2, v2, 0x1

    goto :esc_loop


    :esc_done
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

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
