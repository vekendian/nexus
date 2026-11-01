.class public final Lorg/vekendian/nexus/lua/NexusLua$Modules$Cls;
.super Lluaj/lib/VarArgFunction;
.source "NexusLua.java"


# The __index function of the table nexus.modules.import() returns.
#
# A jar/dex module exposes two things from one value: its @Export methods, which
# the import builder stores as real table keys, and its classes, which are not
# known until something asks for one. This resolves the second kind lazily, so
#     local probe = nexus.modules.import("probe")
#     local p = probe.Probe("hello")
# needs no bindClass call and no dex enumeration.
#
# Key resolution is id-qualified first (id + "." + key), because the module
# id is the package convention install() already uses, then bare (key) for a
# default-package class. A package that does not match the file name stays
# reachable through luajava.bindClass("com.example.Probe"), which
# classForName now also routes through the registered loaders.
#
# A miss is nil, not an error: __index runs for every absent key, including the
# probes a script makes on purpose (`if mod.Maybe then`), so it must not throw.
# An @Export with the same name wins by construction -- it is a real key, and
# __index is only consulted after the raw lookup misses.
#
# invoke() registers: v0 key string, v1 qualified name, v2 class, v3 builder.
#
# The class comes back through CoerceJavaToLua.coerce rather than JavaClass.forClass:
# both live in luaj.lib.jse, but only the former is public, and this class is not.

.field private final id:Ljava/lang/String;


.method public constructor <init>(Ljava/lang/String;)V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/VarArgFunction;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Cls;->id:Ljava/lang/String;

    return-void
.end method


.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 4

    # __index(table, key): the key is argument 2, and a non-string key can never
    # name a class.

    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const/4 v1, 0x2

    invoke-virtual {p1, v1, v0}, Lluaj/Varargs;->d0(ILluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    invoke-virtual {v0}, Lluaj/LuaValue;->n1()Z

    move-result v1

    if-eqz v1, :nil

    invoke-virtual {v0}, Lluaj/LuaValue;->B0()Ljava/lang/String;

    move-result-object v0


    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Modules$Cls;->id:Ljava/lang/String;

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, "."

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lluaj/Hlp;->classForNameInDexes(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    if-eqz v2, :bare


    :found
    # JavaClass is package-private and so is forClass, so a cross-package call to it dies
    # at runtime with IllegalAccessError (the verifier does not catch visibility). Coerce
    # is the public door to the same per-Class cache: a Class coerces to exactly the
    # JavaClass luajava.bindClass hands out, and the declared type here is the public
    # LuaValue, so no package-private type is named at all.
    invoke-static {v2}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0


    :bare
    # if-eqz branches when the register is ZERO (null); if-nez when it is not.
    # The original `if-eqz v2, :found` therefore sent a null class into coerce
    # and a found one into :nil. A miss leaves through :nil; a hit jumps back
    # to the shared coerce block.
    invoke-static {v0}, Lluaj/Hlp;->classForNameInDexes(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    if-eqz v2, :nil

    goto :found


    :nil
    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    return-object v0
.end method
