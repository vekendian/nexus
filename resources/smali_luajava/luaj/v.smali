.class abstract Lluaj/v;
.super Lluaj/Varargs;
.source "src"

# interfaces
.implements Lluaj/ae;


# direct methods
.method constructor <init>()V
    .locals 0

    .prologue
    .line 1220
    invoke-direct {p0}, Lluaj/Varargs;-><init>()V

    return-void
.end method


# virtual methods
.method public abstract a(I)I
.end method

.method public a(Lluaj/ad;)Lluaj/ad;
    .locals 1

    .prologue
    .line 1294
    new-instance v0, Lluaj/aa;

    invoke-direct {v0, p0, p1}, Lluaj/aa;-><init>(Lluaj/v;Lluaj/ad;)V

    return-object v0
.end method

.method public a(Lluaj/ae;)Lluaj/ad;
    .locals 3

    .prologue
    const/4 v2, 0x0

    .line 1299
    new-instance v0, Lluaj/t;

    invoke-virtual {p0}, Lluaj/v;->c()Lluaj/LuaValue;

    move-result-object v1

    invoke-direct {v0, v1, v2, v2}, Lluaj/t;-><init>(Lluaj/LuaValue;Lluaj/ad;Lluaj/t;)V

    return-object v0
.end method

.method public a(Lluaj/ae;Lluaj/LuaValue;)Lluaj/ad;
    .locals 1

    .prologue
    .line 1289
    invoke-virtual {p0, p2}, Lluaj/v;->a_(Lluaj/LuaValue;)Lluaj/v;

    move-result-object v0

    return-object v0
.end method

.method public a()Lluaj/ae;
    .locals 0

    .prologue
    .line 1274
    return-object p0
.end method

.method public call(Lluaj/LuaValue;)Lluaj/ae;
    .locals 1

    .prologue
    .line 1284
    invoke-virtual {p0, p1}, Lluaj/v;->b(Lluaj/LuaValue;)Z

    move-result v0

    if-eqz v0, :cond_0

    :goto_0
    return-object p0

    :cond_0
    const/4 p0, 0x0

    goto :goto_0
.end method

.method abstract a_(Lluaj/LuaValue;)Lluaj/v;
.end method

.method public b(I)I
    .locals 1

    .prologue
    .line 1233
    const/4 v0, 0x0

    return v0
.end method

.method public b(Lluaj/ad;)Lluaj/ad;
    .locals 1

    .prologue
    .line 1304
    if-eqz p1, :cond_0

    new-instance v0, Lluaj/aa;

    invoke-direct {v0, p0, p1}, Lluaj/aa;-><init>(Lluaj/v;Lluaj/ad;)V

    move-object p0, v0

    :cond_0
    return-object p0
.end method

.method public abstract b(Lluaj/LuaValue;)Z
.end method

.method public abstract c()Lluaj/LuaValue;
.end method

.method public c(I)Lluaj/LuaValue;
    .locals 1

    .prologue
    .line 1238
    packed-switch p1, :pswitch_data_0

    .line 1242
    # nexus: pivot init (LuaValue.NIL via LuaTable.u) was dropped by the port;
    # without it the packed-switch default path returns undefined v0
    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    :goto_0
    return-object v0

    .line 1239
    :pswitch_0
    invoke-virtual {p0}, Lluaj/v;->c()Lluaj/LuaValue;

    move-result-object v0

    goto :goto_0

    .line 1240
    :pswitch_1
    invoke-virtual {p0}, Lluaj/v;->t_()Lluaj/LuaValue;

    move-result-object v0

    goto :goto_0

    .line 1238
    :pswitch_data_0
    .packed-switch 0x1
        :pswitch_0
        :pswitch_1
    .end packed-switch
.end method

.method public e0(I)Lluaj/Varargs;
    .locals 0

    .prologue
    .line 1265
    packed-switch p1, :pswitch_data_0

    .line 1269

    :goto_0
    :pswitch_0
    return-object p0

    .line 1267
    :pswitch_1
    invoke-virtual {p0}, Lluaj/v;->t_()Lluaj/LuaValue;

    move-result-object p0

    goto :goto_0

    nop

    :pswitch_data_0
    .packed-switch 0x1
        :pswitch_0
        :pswitch_1
    .end packed-switch
.end method

.method public f()Lluaj/Varargs;
    .locals 0

    .prologue
    .line 1255
    return-object p0
.end method

.method public w()Lluaj/LuaValue;
    .locals 1

    .prologue
    .line 1260
    invoke-virtual {p0}, Lluaj/v;->c()Lluaj/LuaValue;

    move-result-object v0

    return-object v0
.end method

.method public U()I
    .locals 1

    .prologue
    .line 1247
    const/4 v0, 0x2

    return v0
.end method

.method public abstract t_()Lluaj/LuaValue;
.end method

.method public u_()Lluaj/ad;
    .locals 1

    .prologue
    .line 1279
    const/4 v0, 0x0

    return-object v0
.end method
