.class final Lluaj/lib/jse/CoerceJavaToLua$BoolCoercion;
.super Ljava/lang/Object;

# interfaces
.implements Lluaj/lib/jse/CoerceJavaToLua$Coercion;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lluaj/lib/jse/CoerceJavaToLua;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "BoolCoercion"
.end annotation


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public coerce(Ljava/lang/Object;)Lluaj/LuaValue;
    .locals 2

    move-object v0, p1

    check-cast v0, Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v1

    if-eqz v1, :cond_0

    sget-object v1, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    goto :goto_0

    :cond_0
    sget-object v1, Lluaj/LuaValue;->e:Lluaj/LuaBoolean;

    :goto_0
    return-object v1
.end method
