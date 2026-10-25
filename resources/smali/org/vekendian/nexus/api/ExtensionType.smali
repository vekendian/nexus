.class public final enum Lorg/vekendian/nexus/api/ExtensionType;
.super Ljava/lang/Enum;
.source "ExtensionType.java"


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Enum<",
        "Lorg/vekendian/nexus/api/ExtensionType;",
        ">;"
    }
.end annotation


# static fields
.field private static final synthetic $VALUES:[Lorg/vekendian/nexus/api/ExtensionType;

.field public static final enum DEX:Lorg/vekendian/nexus/api/ExtensionType;

.field public static final enum JAR:Lorg/vekendian/nexus/api/ExtensionType;

.field public static final enum LUA:Lorg/vekendian/nexus/api/ExtensionType;


# direct methods
.method private static synthetic $values()[Lorg/vekendian/nexus/api/ExtensionType;
    .registers 3

    const/4 v0, 0x3

    new-array v0, v0, [Lorg/vekendian/nexus/api/ExtensionType;

    .line 6
    sget-object v1, Lorg/vekendian/nexus/api/ExtensionType;->LUA:Lorg/vekendian/nexus/api/ExtensionType;

    const/4 v2, 0x0

    aput-object v1, v0, v2

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionType;->JAR:Lorg/vekendian/nexus/api/ExtensionType;

    const/4 v2, 0x1

    aput-object v1, v0, v2

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionType;->DEX:Lorg/vekendian/nexus/api/ExtensionType;

    const/4 v2, 0x2

    aput-object v1, v0, v2

    return-object v0
.end method

.method static constructor <clinit>()V
    .registers 3

    .line 8
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionType;

    const-string v1, "LUA"

    const/4 v2, 0x0

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionType;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionType;->LUA:Lorg/vekendian/nexus/api/ExtensionType;

    .line 11
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionType;

    const-string v1, "JAR"

    const/4 v2, 0x1

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionType;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionType;->JAR:Lorg/vekendian/nexus/api/ExtensionType;

    .line 14
    new-instance v0, Lorg/vekendian/nexus/api/ExtensionType;

    const-string v1, "DEX"

    const/4 v2, 0x2

    invoke-direct {v0, v1, v2}, Lorg/vekendian/nexus/api/ExtensionType;-><init>(Ljava/lang/String;I)V

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionType;->DEX:Lorg/vekendian/nexus/api/ExtensionType;

    .line 6
    invoke-static {}, Lorg/vekendian/nexus/api/ExtensionType;->$values()[Lorg/vekendian/nexus/api/ExtensionType;

    move-result-object v0

    sput-object v0, Lorg/vekendian/nexus/api/ExtensionType;->$VALUES:[Lorg/vekendian/nexus/api/ExtensionType;

    return-void
.end method

.method private constructor <init>(Ljava/lang/String;I)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 6
    invoke-direct {p0, p1, p2}, Ljava/lang/Enum;-><init>(Ljava/lang/String;I)V

    return-void
.end method

.method public static valueOf(Ljava/lang/String;)Lorg/vekendian/nexus/api/ExtensionType;
    .registers 2

    .line 6
    const-class v0, Lorg/vekendian/nexus/api/ExtensionType;

    invoke-static {v0, p0}, Ljava/lang/Enum;->valueOf(Ljava/lang/Class;Ljava/lang/String;)Ljava/lang/Enum;

    move-result-object p0

    check-cast p0, Lorg/vekendian/nexus/api/ExtensionType;

    return-object p0
.end method

.method public static values()[Lorg/vekendian/nexus/api/ExtensionType;
    .registers 1

    .line 6
    sget-object v0, Lorg/vekendian/nexus/api/ExtensionType;->$VALUES:[Lorg/vekendian/nexus/api/ExtensionType;

    invoke-virtual {v0}, [Lorg/vekendian/nexus/api/ExtensionType;->clone()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, [Lorg/vekendian/nexus/api/ExtensionType;

    return-object v0
.end method
