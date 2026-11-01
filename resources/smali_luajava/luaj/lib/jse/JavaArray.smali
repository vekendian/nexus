.class Lluaj/lib/jse/JavaArray;
.super Lluaj/LuaUserdata;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lluaj/lib/jse/JavaArray$LenFunction;
    }
.end annotation


# static fields
.field static final CLASS:Lluaj/LuaValue;

.field static final LENGTH:Lluaj/LuaValue;

.field static final array_metatable:Lluaj/LuaTable;

.field static final E:Lluaj/LuaString;


# direct methods
.method static constructor <clinit>()V
    .locals 4

    const-string v0, "length"

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    sput-object v0, Lluaj/lib/jse/JavaArray;->LENGTH:Lluaj/LuaValue;

    const-string v0, "class"

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    sput-object v0, Lluaj/lib/jse/JavaArray;->CLASS:Lluaj/LuaValue;

    new-instance v0, Lluaj/LuaTable;

    invoke-direct {v0}, Lluaj/LuaTable;-><init>()V

    sput-object v0, Lluaj/lib/jse/JavaArray;->array_metatable:Lluaj/LuaTable;


    new-instance v2, Lluaj/lib/jse/JavaArray$LenFunction;

    invoke-direct {v2}, Lluaj/lib/jse/JavaArray$LenFunction;-><init>()V

    # nexus: pivot used the __len constant (pivot LuaValue.P) as the metatable key;
    # the port rewrote it to LENGTH ("length"), which drops #arr semantics.
    # Stock name for the __len LuaString is LuaValue.x (clinit-verified).
    sget-object v1, Lluaj/LuaValue;->x:Lluaj/LuaString;

    invoke-virtual {v0, v1, v2}, Lluaj/LuaTable;->d2(Lluaj/LuaValue;Lluaj/LuaValue;)V

    const-string v0, "__newindex"

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    sput-object v0, Lluaj/lib/jse/JavaArray;->E:Lluaj/LuaString;

    return-void
.end method

.method constructor <init>(Ljava/lang/Object;)V
    .locals 1

    invoke-direct {p0, p1}, Lluaj/LuaUserdata;-><init>(Ljava/lang/Object;)V

    sget-object v0, Lluaj/lib/jse/JavaArray;->array_metatable:Lluaj/LuaTable;

    invoke-virtual {p0, v0}, Lluaj/lib/jse/JavaArray;->k2(Lluaj/LuaValue;)Lluaj/LuaValue;

    return-void
.end method


# virtual methods
.method public A(Lluaj/LuaValue;)Lluaj/Varargs;
    .locals 6

    iget-object v0, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-static {v0}, Ljava/lang/reflect/Array;->getLength(Ljava/lang/Object;)I

    move-result v0

    invoke-virtual {p1}, Lluaj/LuaValue;->l1()Z

    move-result v1

    const/4 v2, 0x0

    const/4 v3, 0x1

    if-eqz v1, :cond_0

    move v1, v2

    goto :goto_0

    :cond_0
    invoke-virtual {p1}, Lluaj/LuaValue;->y2()I

    move-result v1

    add-int/2addr v1, v3

    :goto_0
    if-lt v1, v0, :cond_1

    sget-object v2, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    return-object v2

    :cond_1
    const/4 v4, 0x2

    new-array v4, v4, [Lluaj/LuaValue;

    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v5

    invoke-static {v5}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v5

    aput-object v5, v4, v2

    iget-object v2, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-static {v2, v1}, Ljava/lang/reflect/Array;->get(Ljava/lang/Object;I)Ljava/lang/Object;

    move-result-object v2

    invoke-static {v2}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v2

    aput-object v2, v4, v3

    invoke-static {v4}, Lluaj/LuaValue;->O2([Lluaj/LuaValue;)Lluaj/Varargs;

    move-result-object v2

    return-object v2
.end method

.method public j2(Lluaj/LuaValue;Lluaj/LuaValue;)V
    .locals 3

    invoke-virtual {p1}, Lluaj/LuaValue;->j1()Z

    move-result v0

    if-eqz v0, :cond_3

    invoke-virtual {p1}, Lluaj/LuaValue;->y2()I

    move-result v0

    add-int/lit8 v0, v0, -0x1

    if-ltz v0, :cond_0

    iget-object v1, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-static {v1}, Ljava/lang/reflect/Array;->getLength(Ljava/lang/Object;)I

    move-result v1

    if-ge v0, v1, :cond_0

    iget-object v1, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    iget-object v2, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-virtual {v2}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Class;->getComponentType()Ljava/lang/Class;

    move-result-object v2

    invoke-static {p2, v2}, Lluaj/lib/jse/CoerceLuaToJava;->coerce(Lluaj/LuaValue;Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v2

    invoke-static {v1, v0, v2}, Ljava/lang/reflect/Array;->set(Ljava/lang/Object;ILjava/lang/Object;)V

    goto :goto_0

    :cond_0
    iget-object v1, p0, Lluaj/lib/jse/JavaArray;->m_metatable:Lluaj/LuaValue;

    if-eqz v1, :cond_1

    sget-object v1, Lluaj/lib/jse/JavaArray;->E:Lluaj/LuaString;

    iget-object v0, p0, Lluaj/lib/jse/JavaArray;->m_metatable:Lluaj/LuaValue;

    invoke-virtual {v0, v1}, Lluaj/LuaValue;->V1(Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v1

    invoke-virtual {v1}, Lluaj/LuaValue;->l1()Z

    move-result v1

    if-eqz v1, :cond_2

    invoke-static {p0, p1, p2}, Lluaj/LuaValue;->l2(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/LuaValue;)Z

    move-result v1

    if-nez v1, :cond_2

    :cond_1
    const-string v1, "array index out of bounds"

    invoke-static {v1}, Lluaj/LuaValue;->R0(Ljava/lang/String;)Lluaj/LuaValue;

    :cond_2
    :goto_0
    goto :goto_1

    :cond_3
    invoke-super {p0, p1, p2}, Lluaj/LuaUserdata;->j2(Lluaj/LuaValue;Lluaj/LuaValue;)V

    :goto_1
    return-void
.end method

.method public U0(Lluaj/LuaValue;)Lluaj/LuaValue;
    .locals 3

    sget-object v0, Lluaj/lib/jse/JavaArray;->LENGTH:Lluaj/LuaValue;

    invoke-virtual {p1, v0}, Lluaj/LuaValue;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-static {v0}, Ljava/lang/reflect/Array;->getLength(Ljava/lang/Object;)I

    move-result v0

    int-to-long v0, v0

    invoke-static {v0, v1}, Lluaj/LuaValue;->I2(J)Lluaj/LuaLong;

    move-result-object v0

    return-object v0

    :cond_0
    sget-object v0, Lluaj/lib/jse/JavaArray;->CLASS:Lluaj/LuaValue;

    invoke-virtual {p1, v0}, Lluaj/LuaValue;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    iget-object v0, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-virtual {v0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-static {v0}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0

    :cond_1
    invoke-virtual {p1}, Lluaj/LuaValue;->j1()Z

    move-result v0

    if-eqz v0, :cond_3

    invoke-virtual {p1}, Lluaj/LuaValue;->y2()I

    move-result v0

    add-int/lit8 v0, v0, -0x1

    if-ltz v0, :cond_2

    iget-object v1, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-static {v1}, Ljava/lang/reflect/Array;->getLength(Ljava/lang/Object;)I

    move-result v1

    if-ge v0, v1, :cond_2

    iget-object v1, p0, Lluaj/lib/jse/JavaArray;->m_instance:Ljava/lang/Object;

    invoke-virtual {p1}, Lluaj/LuaValue;->y2()I

    move-result v2

    add-int/lit8 v2, v2, -0x1

    invoke-static {v1, v2}, Ljava/lang/reflect/Array;->get(Ljava/lang/Object;I)Ljava/lang/Object;

    move-result-object v1

    invoke-static {v1}, Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;

    move-result-object v1

    goto :goto_0

    :cond_2
    # nexus: pivot init (LuaValue.NIL via JavaArray.u) was dropped by the port;
    # without it the out-of-bounds path returns undefined v1
    sget-object v1, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    :goto_0
    return-object v1

    :cond_3
    invoke-super {p0, p1}, Lluaj/LuaUserdata;->U0(Lluaj/LuaValue;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method
