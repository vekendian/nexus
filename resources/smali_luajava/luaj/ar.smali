.class final Lluaj/ar;
.super Lluaj/Varargs;
.source "src"


# instance fields
.field private final a:[Lluaj/LuaValue;

.field private final b:Lluaj/Varargs;


# direct methods
.method constructor <init>([Lluaj/LuaValue;Lluaj/Varargs;)V
    .locals 0

    .prologue
    .line 580
    invoke-direct {p0}, Lluaj/Varargs;-><init>()V

    .line 581
    iput-object p1, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    .line 582
    iput-object p2, p0, Lluaj/ar;->b:Lluaj/Varargs;

    .line 583
    return-void
.end method


# virtual methods
.method b([Lluaj/LuaValue;II)V
    .locals 3

    .prologue
    .line 606
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v0, v0

    invoke-static {v0, p3}, Ljava/lang/Math;->min(II)I

    move-result v0

    .line 607
    iget-object v1, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    const/4 v2, 0x0

    invoke-static {v1, v2, p1, p2, v0}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 608
    iget-object v1, p0, Lluaj/ar;->b:Lluaj/Varargs;

    add-int v2, p2, v0

    sub-int v0, p3, v0

    invoke-virtual {v1, p1, v2, v0}, Lluaj/Varargs;->L([Lluaj/LuaValue;II)V

    .line 609
    return-void
.end method

.method public c(I)Lluaj/LuaValue;
    .locals 2

    .prologue
    .line 586
    const/4 v0, 0x1

    if-ge p1, v0, :cond_0

    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    :goto_0
    return-object v0

    :cond_0
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v0, v0

    if-gt p1, v0, :cond_1

    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    add-int/lit8 v1, p1, -0x1

    aget-object v0, v0, v1

    goto :goto_0

    :cond_1
    iget-object v0, p0, Lluaj/ar;->b:Lluaj/Varargs;

    iget-object v1, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v1, v1

    sub-int v1, p1, v1

    invoke-virtual {v0, v1}, Lluaj/Varargs;->v(I)Lluaj/LuaValue;

    move-result-object v0

    goto :goto_0
.end method

.method public e0(I)Lluaj/Varargs;
    .locals 4

    .prologue
    const/4 v1, 0x1

    .line 596
    if-gtz p1, :cond_0

    .line 597
    const-string v0, "start must be > 0"

    invoke-static {v1, v0}, Lluaj/LuaValue;->k0(ILjava/lang/String;)Lluaj/LuaValue;

    .line 598
    :cond_0
    if-ne p1, v1, :cond_1

    .line 602
    :goto_0
    return-object p0

    .line 600
    :cond_1
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v0, v0

    if-le p1, v0, :cond_2

    .line 601
    iget-object v0, p0, Lluaj/ar;->b:Lluaj/Varargs;

    iget-object v1, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v1, v1

    sub-int v1, p1, v1

    invoke-virtual {v0, v1}, Lluaj/Varargs;->e0(I)Lluaj/Varargs;

    move-result-object p0

    goto :goto_0

    .line 602
    :cond_2
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    add-int/lit8 v1, p1, -0x1

    iget-object v2, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v2, v2

    add-int/lit8 v3, p1, -0x1

    sub-int/2addr v2, v3

    iget-object v3, p0, Lluaj/ar;->b:Lluaj/Varargs;

    invoke-static {v0, v1, v2, v3}, Lluaj/LuaValue;->Q2([Lluaj/LuaValue;IILluaj/Varargs;)Lluaj/Varargs;

    move-result-object p0

    goto :goto_0
.end method

.method public w()Lluaj/LuaValue;
    .locals 2

    .prologue
    .line 593
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v0, v0

    if-lez v0, :cond_0

    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    const/4 v1, 0x0

    aget-object v0, v0, v1

    :goto_0
    return-object v0

    :cond_0
    iget-object v0, p0, Lluaj/ar;->b:Lluaj/Varargs;

    invoke-virtual {v0}, Lluaj/Varargs;->w()Lluaj/LuaValue;

    move-result-object v0

    goto :goto_0
.end method

.method public U()I
    .locals 2

    .prologue
    .line 590
    iget-object v0, p0, Lluaj/ar;->a:[Lluaj/LuaValue;

    array-length v0, v0

    iget-object v1, p0, Lluaj/ar;->b:Lluaj/Varargs;

    invoke-virtual {v1}, Lluaj/Varargs;->U()I

    move-result v1

    add-int/2addr v0, v1

    return v0
.end method
