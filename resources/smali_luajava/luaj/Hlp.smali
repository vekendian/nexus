.class public Lluaj/Hlp;
.super Ljava/lang/Object;
.source "Hlp.java"

# static fields
.field public static mt:Lluaj/LuaTable;

.field public static dexes:Ljava/util/ArrayList;

.field public static imported:Ljava/util/HashMap;

.field public static G:Lluaj/Globals;

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

# pivot LuaValue.touserdata() base = null; LuaUserdata override = m_instance
.method public static touserdata(Lluaj/LuaValue;)Ljava/lang/Object;
    .locals 1
    instance-of v0, p0, Lluaj/LuaUserdata;
    if-eqz v0, :cond_0
    check-cast p0, Lluaj/LuaUserdata;
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    return-object v0
    :cond_0
    const/4 v0, 0x0
    return-object v0
.end method

# pivot LuaValue.isuserdata() (superchain fallback) = 0; LuaUserdata override = 1
.method public static isuserdata(Lluaj/LuaValue;)Z
    .locals 1
    instance-of v0, p0, Lluaj/LuaUserdata;
    return v0
.end method

# pivot LuaUserdata.checkuserdata() = m_instance; base = typerror
.method public static checkuserdata(Lluaj/LuaValue;)Ljava/lang/Object;
    .locals 1
    instance-of v0, p0, Lluaj/LuaUserdata;
    if-eqz v0, :cond_0
    check-cast p0, Lluaj/LuaUserdata;
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    return-object v0
    :cond_0
    const-string v0, "userdata expected"
    invoke-static {v0}, Lluaj/LuaValue;->R0(Ljava/lang/String;)Lluaj/LuaValue;
    const/4 v0, 0x0
    return-object v0
.end method

# pivot LuaUserdata.checkuserdata(Class): assignable -> m_instance, else typerror(getName())
.method public static checkuserdata(Lluaj/LuaValue;Ljava/lang/Class;)Ljava/lang/Object;
    .locals 1
    instance-of v0, p0, Lluaj/LuaUserdata;
    if-eqz v0, :cond_1
    check-cast p0, Lluaj/LuaUserdata;
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    invoke-virtual {v0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;
    move-result-object v0
    invoke-virtual {p1, v0}, Ljava/lang/Class;->isAssignableFrom(Ljava/lang/Class;)Z
    move-result v0
    if-eqz v0, :cond_1
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    return-object v0
    :cond_1
    invoke-virtual {p1}, Ljava/lang/Class;->getName()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lluaj/LuaValue;->R0(Ljava/lang/String;)Lluaj/LuaValue;
    const/4 v0, 0x0
    return-object v0
.end method

# pivot LuaValue.raweq(LuaUserdata) base = false; LuaUserdata body: ref-eq or (mt ref-eq and instance equals)
.method public static raweq(Lluaj/LuaValue;Lluaj/LuaUserdata;)Z
    .locals 2
    instance-of v0, p0, Lluaj/LuaUserdata;
    if-eqz v0, :cond_0
    if-eq p0, p1, :cond_1
    check-cast p0, Lluaj/LuaUserdata;
    iget-object v0, p0, Lluaj/LuaUserdata;->m_metatable:Lluaj/LuaValue;
    iget-object v1, p1, Lluaj/LuaUserdata;->m_metatable:Lluaj/LuaValue;
    if-ne v0, v1, :cond_0
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    iget-object v1, p1, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    invoke-virtual {v0, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :cond_1
    :cond_0
    const/4 v0, 0x0
    return v0
    :cond_1
    const/4 v0, 0x1
    return v0
.end method

# pivot eqmtcall (decl missing in P tree; reconstructed from stock LuaValue.Q0 machinery):
# op = lsmt.rawget(__eq); if isnil -> rsmt.rawget(__eq); if isnil -> false; else op.call(lhs,rhs).toboolean()
.method public static eqmtcall(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/LuaValue;)Z
    .locals 2
    sget-object v0, Lluaj/LuaValue;->y:Lluaj/LuaString;
    invoke-virtual {p1, v0}, Lluaj/LuaValue;->V1(Lluaj/LuaValue;)Lluaj/LuaValue;
    move-result-object v0
    invoke-virtual {v0}, Lluaj/LuaValue;->l1()Z
    move-result v1
    if-eqz v1, :cond_0
    sget-object v0, Lluaj/LuaValue;->y:Lluaj/LuaString;
    invoke-virtual {p3, v0}, Lluaj/LuaValue;->V1(Lluaj/LuaValue;)Lluaj/LuaValue;
    move-result-object v0
    :cond_0
    invoke-virtual {v0}, Lluaj/LuaValue;->l1()Z
    move-result v1
    if-eqz v1, :cond_1
    const/4 v0, 0x0
    return v0
    :cond_1
    invoke-virtual {v0, p0, p2}, Lluaj/LuaValue;->call(Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/LuaValue;
    move-result-object v0
    invoke-virtual {v0}, Lluaj/LuaValue;->w2()Z
    move-result v0
    return v0
.end method

# pivot LuaUserdata.optuserdata(Class,Object): assignable -> m_instance else typerror(getName())
.method public static optuserdata(Lluaj/LuaValue;Ljava/lang/Class;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1
    instance-of v0, p0, Lluaj/LuaUserdata;
    if-eqz v0, :cond_0
    check-cast p0, Lluaj/LuaUserdata;
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    invoke-virtual {v0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;
    move-result-object v0
    invoke-virtual {p1, v0}, Ljava/lang/Class;->isAssignableFrom(Ljava/lang/Class;)Z
    move-result v0
    if-eqz v0, :cond_0
    iget-object v0, p0, Lluaj/LuaUserdata;->m_instance:Ljava/lang/Object;
    return-object v0
    :cond_0
    invoke-virtual {p1}, Ljava/lang/Class;->getName()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lluaj/LuaValue;->R0(Ljava/lang/String;)Lluaj/LuaValue;
    const/4 v0, 0x0
    return-object v0
.end method

# pivot LuaValue.userdataOf(Object) = new LuaUserdata(instance)
.method public static userdataOf(Ljava/lang/Object;)Lluaj/LuaUserdata;
    .locals 1
    new-instance v0, Lluaj/LuaUserdata;
    invoke-direct {v0, p0}, Lluaj/LuaUserdata;-><init>(Ljava/lang/Object;)V
    return-object v0
.end method

# pivot ap-side Varargs.isuserdata(i) = arg(i).isuserdata()
.method public static isuserdataV(Lluaj/Varargs;I)Z
    .locals 2
    invoke-virtual {p0, p1}, Lluaj/Varargs;->v(I)Lluaj/LuaValue;
    move-result-object v0
    instance-of v1, v0, Lluaj/LuaUserdata;
    return v1
.end method

# pivot ap-side Varargs.checkuserdata(i) = arg(i).checkuserdata()
.method public static checkuserdataV(Lluaj/Varargs;I)Ljava/lang/Object;
    .locals 1
    invoke-virtual {p0, p1}, Lluaj/Varargs;->v(I)Lluaj/LuaValue;
    move-result-object v0
    invoke-static {v0}, Lluaj/Hlp;->checkuserdata(Lluaj/LuaValue;)Ljava/lang/Object;
    move-result-object v0
    return-object v0
.end method

# pivot call-site shim: fn.invoke(arg) == real luaj invoke(LuaValue,Varargs) with NONE tail
# (invoke(arg,varargs) = invoke(varargsOf(arg,varargs)); stock LuaValue.f = public static final NONE)
.method public static invoke1(Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/Varargs;
    .locals 1
    sget-object v0, Lluaj/LuaValue;->f:Lluaj/LuaValue;
    invoke-virtual {p0, p1, v0}, Lluaj/LuaValue;->invoke(Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;
    move-result-object v0
    return-object v0
.end method

.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    sput-object v0, Lluaj/Hlp;->mt:Lluaj/LuaTable;

    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    sput-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    sput-object v0, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    return-void
.end method

# dotted-path set: G.a.b.leaf = value (auto-creates intermediate tables)
.method public static At(Ljava/lang/String;Lluaj/LuaValue;)V
    .locals 8

    const-string v0, "[.]"

    invoke-virtual {p0, v0}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    array-length v1, v0

    if-eqz v1, :return

    const/4 v2, 0x1

    if-ne v1, v2, :multi

    # single segment
    sget-object v3, Lluaj/Hlp;->G:Lluaj/Globals;

    const/4 v4, 0x0

    aget-object v4, v0, v4

    invoke-static {v4}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v4

    invoke-virtual {v3, v4, p1}, Lluaj/LuaValue;->j2(Lluaj/LuaValue;Lluaj/LuaValue;)V

    goto :return

    :multi
    new-array v2, v1, [Lluaj/LuaValue;

    sget-object v3, Lluaj/Hlp;->G:Lluaj/Globals;

    const/4 v4, 0x0

    aput-object v3, v2, v4

    const/4 v3, 0x1

    :loop
    if-ge v3, v1, :leaf

    add-int/lit8 v4, v3, -0x1

    aget-object v4, v2, v4

    add-int/lit8 v5, v3, -0x1

    aget-object v5, v0, v5

    invoke-static {v5}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v5

    invoke-virtual {v4, v5}, Lluaj/LuaValue;->U0(Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v6

    sget-object v7, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    if-ne v6, v7, :store

    new-instance v6, Lluaj/LuaTable;

    invoke-direct {v6}, Lluaj/LuaTable;-><init>()V

    invoke-virtual {v4, v5, v6}, Lluaj/LuaValue;->j2(Lluaj/LuaValue;Lluaj/LuaValue;)V

    :store
    aput-object v6, v2, v3

    add-int/lit8 v3, v3, 0x1

    goto :loop

    :leaf
    add-int/lit8 v3, v1, -0x1

    aget-object v3, v2, v3

    add-int/lit8 v4, v1, -0x1

    aget-object v4, v0, v4

    invoke-static {v4}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v4

    invoke-virtual {v3, v4, p1}, Lluaj/LuaValue;->j2(Lluaj/LuaValue;Lluaj/LuaValue;)V

    :return
    return-void
.end method

# convert additions Prototype (al) -> stock Prototype (h)
.method public static proto(Lluaj/al;)Lluaj/h;
    .locals 10

    new-instance v0, Lluaj/h;

    invoke-direct {v0}, Lluaj/h;-><init>()V

    iget-object v1, p0, Lluaj/al;->q:[Lluaj/LuaValue;

    iput-object v1, v0, Lluaj/h;->a:[Lluaj/LuaValue;

    iget-object v1, p0, Lluaj/al;->r:[I

    iput-object v1, v0, Lluaj/h;->b:[I

    iget-object v1, p0, Lluaj/al;->t:[I

    iput-object v1, v0, Lluaj/h;->d:[I

    iget-object v1, p0, Lluaj/al;->w:Lluaj/LuaString;

    iput-object v1, v0, Lluaj/h;->g:Lluaj/LuaString;

    iget v1, p0, Lluaj/al;->x:I

    iput v1, v0, Lluaj/h;->h:I

    iget v1, p0, Lluaj/al;->y:I

    iput v1, v0, Lluaj/h;->i:I

    iget v1, p0, Lluaj/al;->z:I

    iput v1, v0, Lluaj/h;->j:I

    iget v1, p0, Lluaj/al;->A:I

    iput v1, v0, Lluaj/h;->k:I

    iget v1, p0, Lluaj/al;->B:I

    iput v1, v0, Lluaj/h;->l:I

    iget v1, p0, Lluaj/al;->C:I

    iput v1, v0, Lluaj/h;->m:I

    # locals e:[Lf/b  <-  u:[Lluaj/l;
    iget-object v1, p0, Lluaj/al;->u:[Lluaj/l;

    if-eqz v1, :no_local

    array-length v2, v1

    new-array v3, v2, [Lf/b;

    const/4 v4, 0x0

    :loc_loop
    if-ge v4, v2, :loc_store

    aget-object v5, v1, v4

    new-instance v6, Lf/b;

    iget-object v7, v5, Lluaj/l;->a:Lluaj/LuaString;

    iget v8, v5, Lluaj/l;->b:I

    iget v9, v5, Lluaj/l;->c:I

    invoke-direct {v6, v7, v8, v9}, Lf/b;-><init>(Lluaj/LuaString;II)V

    aput-object v6, v3, v4

    add-int/lit8 v4, v4, 0x1

    goto :loc_loop

    :loc_store
    iput-object v3, v0, Lluaj/h;->e:[Lf/b;

    :no_local
    # upvalues f:[Lf/d  <-  v:[Lluaj/ao;
    iget-object v1, p0, Lluaj/al;->v:[Lluaj/ao;

    if-eqz v1, :no_uv

    array-length v2, v1

    new-array v3, v2, [Lf/d;

    const/4 v4, 0x0

    :uv_loop
    if-ge v4, v2, :uv_store

    aget-object v5, v1, v4

    new-instance v6, Lf/d;

    iget-object v7, v5, Lluaj/ao;->a:Lluaj/LuaString;

    iget-boolean v8, v5, Lluaj/ao;->b:Z

    iget-short v9, v5, Lluaj/ao;->c:S

    invoke-direct {v6, v7, v8, v9}, Lf/d;-><init>(Lluaj/LuaString;ZI)V

    aput-object v6, v3, v4

    add-int/lit8 v4, v4, 0x1

    goto :uv_loop

    :uv_store
    iput-object v3, v0, Lluaj/h;->f:[Lf/d;

    :no_uv
    # nested prototypes c:[h  <-  s:[Lluaj/al;   (recurse)
    iget-object v1, p0, Lluaj/al;->s:[Lluaj/al;

    if-eqz v1, :no_proto

    array-length v2, v1

    new-array v3, v2, [Lluaj/h;

    const/4 v4, 0x0

    :pr_loop
    if-ge v4, v2, :pr_store

    aget-object v5, v1, v4

    invoke-static {v5}, Lluaj/Hlp;->proto(Lluaj/al;)Lluaj/h;

    move-result-object v6

    aput-object v6, v3, v4

    add-int/lit8 v4, v4, 0x1

    goto :pr_loop

    :pr_store
    iput-object v3, v0, Lluaj/h;->c:[Lluaj/h;

    :no_proto
    return-object v0
.end method

.method public static f(Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/v;
    .locals 6

    .prologue
    .line 1410
    invoke-virtual {p0}, Lluaj/LuaValue;->i1()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 1411
    new-instance v0, Lluaj/x;

    invoke-virtual {p0}, Lluaj/LuaValue;->A0()I

    move-result v1

    invoke-direct {v0, v1, p1}, Lluaj/x;-><init>(ILluaj/LuaValue;)V

    .line 1426
    :goto_0
    return-object v0

    .line 1412
    :cond_0
    instance-of v0, p1, Lluaj/LuaBoolean;

    if-eqz v0, :cond_1

    .line 1413
    new-instance v0, Lluaj/s;

    invoke-virtual {p1}, Lluaj/LuaValue;->w2()Z

    move-result v1

    invoke-direct {v0, p0, v1}, Lluaj/s;-><init>(Lluaj/LuaValue;Z)V

    goto :goto_0

    .line 1415
    :cond_1
    instance-of v0, p1, Lluaj/LuaLong;

    if-eqz v0, :cond_3

    .line 1416
    invoke-virtual {p1}, Lluaj/LuaValue;->C0()J

    move-result-wide v2

    .line 1417
    long-to-int v1, v2

    .line 1418
    int-to-long v4, v1

    cmp-long v0, v4, v2

    if-nez v0, :cond_2

    new-instance v0, Lluaj/y;

    invoke-direct {v0, p0, v1}, Lluaj/y;-><init>(Lluaj/LuaValue;I)V

    goto :goto_0

    .line 1419
    :cond_2
    new-instance v0, Lluaj/ab;

    invoke-direct {v0, p0, v2, v3}, Lluaj/ab;-><init>(Lluaj/LuaValue;J)V

    goto :goto_0

    .line 1420
    :cond_3
    instance-of v0, p1, Lluaj/LuaDouble;

    if-eqz v0, :cond_5

    .line 1421
    invoke-virtual {p1}, Lluaj/LuaValue;->x2()D

    move-result-wide v2

    .line 1422
    double-to-float v1, v2

    .line 1423
    float-to-double v4, v1

    cmpl-double v0, v4, v2

    if-nez v0, :cond_4

    new-instance v0, Lluaj/w;

    invoke-direct {v0, p0, v1}, Lluaj/w;-><init>(Lluaj/LuaValue;F)V

    goto :goto_0

    .line 1424
    :cond_4
    new-instance v0, Lluaj/u;

    invoke-direct {v0, p0, v2, v3}, Lluaj/u;-><init>(Lluaj/LuaValue;D)V

    goto :goto_0

    .line 1426
    :cond_5
    new-instance v0, Lluaj/ac;

    invoke-direct {v0, p0, p1}, Lluaj/ac;-><init>(Lluaj/LuaValue;Lluaj/LuaValue;)V

    goto :goto_0
.end method

.method public static ImportExecute(Ljava/lang/String;)Lluaj/LuaValue;
    .locals 5

    sget-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_0

    sget-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I

    move-result v0

    add-int/lit8 v1, v0, -0x1

    :goto_0
    if-ltz v1, :cond_0

    :try_start_0
    sget-object v2, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v2, v1}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ldalvik/system/DexClassLoader;

    invoke-virtual {v2, p0}, Ldalvik/system/DexClassLoader;->loadClass(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    sget-object v3, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v3, p0, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    invoke-static {v2}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v3

    invoke-virtual {v2}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4, v3}, Lluaj/Hlp;->At(Ljava/lang/String;Lluaj/LuaValue;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object v3

    :catch_0
    move-exception v2

    invoke-virtual {v2}, Ljava/lang/Exception;->printStackTrace()V

    add-int/lit8 v1, v1, -0x1

    goto :goto_0

    :cond_0
    sget-object v0, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v0}, Ljava/util/HashMap;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_3

    sget-object v0, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v0, p0}, Ljava/util/HashMap;->containsKey(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_1

    goto :goto_1

    :cond_1
    sget-object v0, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v0, p0}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/lang/Class;

    if-eqz v0, :cond_2

    invoke-static {v0}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v1

    invoke-virtual {v0}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2, v1}, Lluaj/Hlp;->At(Ljava/lang/String;Lluaj/LuaValue;)V

    return-object v1

    :cond_2
    :try_start_1
    invoke-static {p0}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    move-object v0, v1

    sget-object v1, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v1, p0, v0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    invoke-static {v0}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v1

    invoke-virtual {v0}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2, v1}, Lluaj/Hlp;->At(Ljava/lang/String;Lluaj/LuaValue;)V
    :try_end_1
    .catch Ljava/lang/ClassNotFoundException; {:try_start_1 .. :try_end_1} :catch_1

    return-object v1

    :catch_1
    move-exception v1

    invoke-virtual {v1}, Ljava/lang/ClassNotFoundException;->printStackTrace()V

    goto :goto_2

    :cond_3
    :goto_1
    :try_start_2
    invoke-static {p0}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v0

    sget-object v1, Lluaj/Hlp;->imported:Ljava/util/HashMap;

    invoke-virtual {v1, p0, v0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    invoke-static {v0}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v1

    invoke-virtual {v0}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2, v1}, Lluaj/Hlp;->At(Ljava/lang/String;Lluaj/LuaValue;)V
    :try_end_2
    .catch Ljava/lang/ClassNotFoundException; {:try_start_2 .. :try_end_2} :catch_2

    return-object v1

    :catch_2
    move-exception v0

    invoke-virtual {v0}, Ljava/lang/ClassNotFoundException;->printStackTrace()V

    nop

    :goto_2
    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    return-object v0
.end method


# Silent class lookup across every registered extension loader, most recently
# imported first so a newer module shadows an older one. Returns null on a miss:
# the Lua resolver turns that into nil, luajava.bindClass into a
# ClassNotFoundException. Throwable, not Exception, because a loader closed by
# uninstall throws IllegalStateException and a bad dex throws LinkageError --
# both are misses, not reasons to abort the walk.
#
# v0 size, v1 index, v2 loader, v3 class.

.method public static classForNameInDexes(Ljava/lang/String;)Ljava/lang/Class;
    .locals 4

    sget-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I

    move-result v0

    add-int/lit8 v1, v0, -0x1

    :loop
    if-ltz v1, :miss

    :try_start
    sget-object v2, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v2, v1}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/ClassLoader;

    invoke-virtual {v2, p0}, Ljava/lang/ClassLoader;->loadClass(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v3
    :try_end
    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :next

    return-object v3

    :next
    add-int/lit8 v1, v1, -0x1

    goto :loop

    :miss
    const/4 v3, 0x0

    return-object v3
.end method


# Idempotent: importing one extension twice must not grow the list, and a null
# loader (a .lua extension, or a jar that failed to prepare) is not an error --
# the caller only registers what the engine actually handed back.

.method public static registerDex(Ljava/lang/ClassLoader;)V
    .locals 1

    if-eqz p0, :return

    sget-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v0, p0}, Ljava/util/ArrayList;->contains(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :return

    sget-object v0, Lluaj/Hlp;->dexes:Ljava/util/ArrayList;

    invoke-virtual {v0, p0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    :return
    return-void
.end method


.method public static zq(I)Ljava/lang/String;
    .locals 3

    :try_start_0
    sget-object v0, Landroid/ext/r;->o:Landroid/content/Context;

    invoke-static {v0}, Landroid/ext/Tools;->l1(Landroid/content/Context;)Landroid/content/Context;

    move-result-object v0

    invoke-virtual {v0, p0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-object v1

    :catch_0
    move-exception v0

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "(Invalid resource id "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ")"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    return-object v1
.end method
