.class public final enum Lorg/vekendian/nexus/api/ExtensionInfo$Type;
.super Ljava/lang/Enum;
.source "ExtensionInfo.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lorg/vekendian/nexus/api/ExtensionInfo;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x4019
    name = "Type"
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Enum<",
        "Lorg/vekendian/nexus/api/ExtensionInfo$Type;",
        ">;"
    }
.end annotation


# static fields
.field private static final synthetic $VALUES:[Lorg/vekendian/nexus/api/ExtensionInfo$Type;

.field public static final enum DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

.field public static final enum JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

.field public static final enum LUA:Lorg/vekendian/nexus/api/ExtensionInfo$Type;


# direct methods
.method private static synthetic $values()[Lorg/vekendian/nexus/api/ExtensionInfo$Type;
    .registers 3

    const/4 v0, 0x3

    new-array v0, v0, [Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    .line 20
    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->LUA:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const/4 v2, 0x0

    aput-object v1, v0, v2

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const/4 v2, 0x1

    aput-object v1, v0, v2

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const/4 v2, 0x2

    aput-object v1, v0, v2

    return-object v0
.end method

.method static constructor <clinit>()V
    .registers 3

    .line 21
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const-string v1, "LUA"

    const/4 v2, 0x0

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionInfo$Type;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->LUA:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    .line 22
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const-string v1, "JAR"

    const/4 v2, 0x1

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionInfo$Type;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    .line 23
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const-string v1, "DEX"

    const/4 v2, 0x2

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionInfo$Type;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    .line 20
    invoke-static {}, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->$values()[Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v0

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->$VALUES:[Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    return-void
.end method

.method private constructor <init>(Ljava/lang/String;I)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 20
    invoke-direct {p0, p1, p2}, Ljava/lang/Enum;-><init>(Ljava/lang/String;I)V

    return-void
.end method

.method public static valueOf(Ljava/lang/String;)Lorg/vekendian/nexus/api/ExtensionInfo$Type;
    .registers 2

    .line 20
    const-class v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    invoke-static {v0, p0}, Ljava/lang/Enum;->valueOf(Ljava/lang/Class;Ljava/lang/String;)Ljava/lang/Enum;

    move-result-object p0

    check-cast p0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    return-object p0
.end method

.method public static values()[Lorg/vekendian/nexus/api/ExtensionInfo$Type;
    .registers 1

    .line 20
    sget-object v0, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->$VALUES:[Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    invoke-virtual {v0}, [Lorg/vekendian/nexus/api/ExtensionInfo$Type;->clone()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, [Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    return-object v0
.end method
