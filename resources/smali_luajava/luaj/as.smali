.class final Lluaj/as;
.super Lluaj/Varargs;
.source "src"


# instance fields
.field private final a:Lluaj/LuaValue;

.field private final b:Lluaj/Varargs;


# direct methods
.method constructor <init>(Lluaj/LuaValue;Lluaj/Varargs;)V
    .locals 0

    .prologue
    .line 533
    invoke-direct {p0}, Lluaj/Varargs;-><init>()V

    .line 534
    iput-object p1, p0, Lluaj/as;->a:Lluaj/LuaValue;

    .line 535
    iput-object p2, p0, Lluaj/as;->b:Lluaj/Varargs;

    .line 536
    return-void
.end method


# virtual methods
.method public c(I)Lluaj/LuaValue;
    .locals 2

    .prologue
    .line 539
    const/4 v0, 0x1

    if-ne p1, v0, :cond_0

    iget-object v0, p0, Lluaj/as;->a:Lluaj/LuaValue;

    :goto_0
    return-object v0

    :cond_0
    iget-object v0, p0, Lluaj/as;->b:Lluaj/Varargs;

    add-int/lit8 v1, p1, -0x1

    invoke-virtual {v0, v1}, Lluaj/Varargs;->v(I)Lluaj/LuaValue;

    move-result-object v0

    goto :goto_0
.end method

.method public e0(I)Lluaj/Varargs;
    .locals 2

    .prologue
    const/4 v0, 0x2

    const/4 v1, 0x1

    .line 551
    if-ne p1, v1, :cond_0

    .line 557
    :goto_0
    return-object p0

    .line 553
    :cond_0
    if-ne p1, v0, :cond_1

    .line 554
    iget-object p0, p0, Lluaj/as;->b:Lluaj/Varargs;

    goto :goto_0

    .line 555
    :cond_1
    if-le p1, v0, :cond_2

    .line 556
    iget-object v0, p0, Lluaj/as;->b:Lluaj/Varargs;

    add-int/lit8 v1, p1, -0x1

    invoke-virtual {v0, v1}, Lluaj/Varargs;->e0(I)Lluaj/Varargs;

    move-result-object p0

    goto :goto_0

    .line 557
    :cond_2
    const-string v0, "start must be > 0"

    invoke-static {v1, v0}, Lluaj/LuaValue;->k0(ILjava/lang/String;)Lluaj/LuaValue;

    move-result-object p0

    goto :goto_0
.end method

.method public w()Lluaj/LuaValue;
    .locals 1

    .prologue
    .line 547
    iget-object v0, p0, Lluaj/as;->a:Lluaj/LuaValue;

    return-object v0
.end method

.method public U()I
    .locals 1

    .prologue
    .line 543
    iget-object v0, p0, Lluaj/as;->b:Lluaj/Varargs;

    invoke-virtual {v0}, Lluaj/Varargs;->U()I

    move-result v0

    add-int/lit8 v0, v0, 0x1

    return v0
.end method
