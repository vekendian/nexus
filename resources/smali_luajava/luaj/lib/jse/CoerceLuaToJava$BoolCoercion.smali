.class final Lluaj/lib/jse/CoerceLuaToJava$BoolCoercion;
.super Ljava/lang/Object;

# interfaces
.implements Lluaj/lib/jse/CoerceLuaToJava$Coercion;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lluaj/lib/jse/CoerceLuaToJava;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x18
    name = "BoolCoercion"
.end annotation


# direct methods
.method constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public coerce(Lluaj/LuaValue;)Ljava/lang/Object;
    .locals 1

    invoke-virtual {p1}, Lluaj/LuaValue;->w2()Z

    move-result v0

    if-eqz v0, :cond_0

    sget-object v0, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;

    goto :goto_0

    :cond_0
    sget-object v0, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    :goto_0
    return-object v0
.end method

.method public score(Lluaj/LuaValue;)I
    .locals 1

    invoke-virtual {p1}, Lluaj/LuaValue;->C2()I

    move-result v0

    packed-switch v0, :pswitch_data_0

    const/16 v0, 0x20

    return v0

    :pswitch_0
    const/4 v0, 0x0

    return v0

    :pswitch_data_0
    .packed-switch 0x1
        :pswitch_0
    .end packed-switch
.end method

.method public toString()Ljava/lang/String;
    .locals 1

    const-string v0, "BoolCoercion()"

    return-object v0
.end method
