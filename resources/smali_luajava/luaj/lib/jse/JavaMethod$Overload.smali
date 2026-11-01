.class Lluaj/lib/jse/JavaMethod$Overload;
.super Lluaj/LuaFunction;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lluaj/lib/jse/JavaMethod;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x8
    name = "Overload"
.end annotation


# instance fields
.field final methods:[Lluaj/lib/jse/JavaMethod;

.field public uservalue:Lluaj/LuaValue;


# direct methods
.method constructor <init>([Lluaj/lib/jse/JavaMethod;)V
    .locals 0

    invoke-direct {p0}, Lluaj/LuaFunction;-><init>()V

    iput-object p1, p0, Lluaj/lib/jse/JavaMethod$Overload;->methods:[Lluaj/lib/jse/JavaMethod;

    return-void
.end method

.method private invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;
    .locals 5

    const/4 v0, 0x0

    sget v1, Lluaj/lib/jse/CoerceLuaToJava;->SCORE_UNCOERCIBLE:I

    const/4 v2, 0x0

    :goto_0
    iget-object v3, p0, Lluaj/lib/jse/JavaMethod$Overload;->methods:[Lluaj/lib/jse/JavaMethod;

    array-length v4, v3

    if-ge v2, v4, :cond_1

    aget-object v3, v3, v2

    invoke-virtual {v3, p2}, Lluaj/lib/jse/JavaMethod;->score(Lluaj/Varargs;)I

    move-result v3

    if-ge v3, v1, :cond_0

    move v1, v3

    iget-object v4, p0, Lluaj/lib/jse/JavaMethod$Overload;->methods:[Lluaj/lib/jse/JavaMethod;

    aget-object v0, v4, v2

    if-nez v1, :cond_0

    goto :goto_1

    :cond_0
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    :cond_1
    :goto_1
    if-nez v0, :cond_2

    const-string v2, "no coercible public method"

    invoke-static {v2}, Lluaj/LuaValue;->R0(Ljava/lang/String;)Lluaj/LuaValue;

    :cond_2
    iget-object v2, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    invoke-virtual {v0, v2}, Lluaj/lib/jse/JavaMethod;->setuservalue(Lluaj/LuaValue;)V

    invoke-virtual {v0, p1, p2}, Lluaj/lib/jse/JavaMethod;->invokeMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v2

    return-object v2
.end method


# virtual methods
.method public call(Lluaj/LuaValue;)Lluaj/LuaValue;
    .locals 2

    iget-object v0, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    if-eq p1, v0, :cond_drop

    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    invoke-direct {p0, v0, p1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0

    :cond_drop
    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    sget-object v1, Lluaj/LuaValue;->f:Lluaj/LuaValue;

    invoke-direct {p0, v0, v1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public call(Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/LuaValue;
    .locals 2

    iget-object v0, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    if-eq p1, v0, :cond_drop

    invoke-static {p1, p2}, Lluaj/LuaValue;->N2(Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object v1

    goto :cond_invoke

    :cond_drop
    move-object v1, p2

    :cond_invoke
    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    invoke-direct {p0, v0, v1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public call(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/LuaValue;
    .locals 2

    iget-object v0, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    if-eq p1, v0, :cond_drop

    invoke-static {p1, p2, p3}, Lluaj/LuaValue;->M2(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object v1

    goto :cond_invoke

    :cond_drop
    invoke-static {p2, p3}, Lluaj/LuaValue;->N2(Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object v1

    :cond_invoke
    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    invoke-direct {p0, v0, v1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public a([Lluaj/LuaValue;)Lluaj/Varargs;
    .locals 1

    invoke-static {p1}, Lluaj/LuaValue;->O2([Lluaj/LuaValue;)Lluaj/Varargs;

    move-result-object v0

    invoke-virtual {p0, v0}, Lluaj/lib/jse/JavaMethod$Overload;->invoke(Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object v0

    return-object v0
.end method

.method public invoke(Lluaj/Varargs;)Lluaj/Varargs;
    .locals 3

    iget-object v0, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    invoke-virtual {p1}, Lluaj/Varargs;->U()I

    move-result v1

    if-lez v1, :cond_keep

    const/4 v2, 0x1

    invoke-virtual {p1, v2}, Lluaj/Varargs;->v(I)Lluaj/LuaValue;

    move-result-object v1

    if-ne v1, v0, :cond_keep

    const/4 v2, 0x2

    invoke-virtual {p1, v2}, Lluaj/Varargs;->e0(I)Lluaj/Varargs;

    move-result-object p1

    :cond_keep
    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    invoke-direct {p0, v0, p1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public call()Lluaj/LuaValue;
    .locals 2

    iget-object v0, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    invoke-static {v0}, Lluaj/Hlp;->touserdata(Lluaj/LuaValue;)Ljava/lang/Object;

    move-result-object v0

    sget-object v1, Lluaj/LuaValue;->f:Lluaj/LuaValue;

    invoke-direct {p0, v0, v1}, Lluaj/lib/jse/JavaMethod$Overload;->invokeBestMethod(Ljava/lang/Object;Lluaj/Varargs;)Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public setuservalue(Lluaj/LuaValue;)V
    .locals 0

    iput-object p1, p0, Lluaj/lib/jse/JavaMethod$Overload;->uservalue:Lluaj/LuaValue;

    return-void
.end method
