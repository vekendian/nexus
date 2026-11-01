.class public final Lorg/vekendian/nexus/api/ModuleInfo;
.super Ljava/lang/Object;
.source "ModuleInfo.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/vekendian/nexus/api/ModuleInfo$Type;
    }
.end annotation


# static fields
.field public static final STATE_ERROR:I = 0x4

.field public static final STATE_FINISHED:I = 0x2

.field public static final STATE_IDLE:I = 0x0

.field public static final STATE_RUNNING:I = 0x1

.field public static final STATE_STOPPED:I = 0x3


# instance fields
.field private final autostart:Z

.field private final dependsOn:[Ljava/lang/String;

.field private final description:Ljava/lang/String;

.field private final message:Ljava/lang/String;

.field private final name:Ljava/lang/String;

.field private final path:Ljava/lang/String;

.field private final size:J

.field private final state:I

.field private final type:Lorg/vekendian/nexus/api/ModuleInfo$Type;

.field private final version:I


# direct methods
.method public constructor <init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IILjava/lang/String;JZ)V
    .registers 22

    .line 56
    sget-object v10, Lorg/vekendian/nexus/api/ModuleInfo$Type;->LUA:Lorg/vekendian/nexus/api/ModuleInfo$Type;

    const/4 v0, 0x0

    new-array v11, v0, [Ljava/lang/String;

    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    move-object v3, p3

    move/from16 v4, p4

    move/from16 v5, p5

    move-object/from16 v6, p6

    move-wide/from16 v7, p7

    move/from16 v9, p9

    invoke-direct/range {v0 .. v11}, Lorg/vekendian/nexus/api/ModuleInfo;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IILjava/lang/String;JZLorg/vekendian/nexus/api/ModuleInfo$Type;[Ljava/lang/String;)V

    return-void
.end method

.method public constructor <init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IILjava/lang/String;JZLorg/vekendian/nexus/api/ModuleInfo$Type;[Ljava/lang/String;)V
    .registers 12

    .line 40
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 41
    iput-object p1, p0, Lorg/vekendian/nexus/api/ModuleInfo;->path:Ljava/lang/String;

    .line 42
    iput-object p2, p0, Lorg/vekendian/nexus/api/ModuleInfo;->name:Ljava/lang/String;

    .line 43
    iput-object p3, p0, Lorg/vekendian/nexus/api/ModuleInfo;->description:Ljava/lang/String;

    .line 44
    iput p4, p0, Lorg/vekendian/nexus/api/ModuleInfo;->version:I

    .line 45
    iput p5, p0, Lorg/vekendian/nexus/api/ModuleInfo;->state:I

    .line 46
    iput-object p6, p0, Lorg/vekendian/nexus/api/ModuleInfo;->message:Ljava/lang/String;

    .line 47
    iput-wide p7, p0, Lorg/vekendian/nexus/api/ModuleInfo;->size:J

    .line 48
    iput-boolean p9, p0, Lorg/vekendian/nexus/api/ModuleInfo;->autostart:Z

    if-eqz p10, :cond_16

    goto :goto_18

    .line 49
    :cond_16
    sget-object p10, Lorg/vekendian/nexus/api/ModuleInfo$Type;->LUA:Lorg/vekendian/nexus/api/ModuleInfo$Type;

    :goto_18
    iput-object p10, p0, Lorg/vekendian/nexus/api/ModuleInfo;->type:Lorg/vekendian/nexus/api/ModuleInfo$Type;

    if-eqz p11, :cond_1d

    goto :goto_20

    :cond_1d
    const/4 p1, 0x0

    new-array p11, p1, [Ljava/lang/String;

    .line 50
    :goto_20
    iput-object p11, p0, Lorg/vekendian/nexus/api/ModuleInfo;->dependsOn:[Ljava/lang/String;

    return-void
.end method


# virtual methods
.method public autostart()Z
    .registers 2

    .line 94
    iget-boolean v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->autostart:Z

    return v0
.end method

.method public dependsOn()[Ljava/lang/String;
    .registers 2

    .line 104
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->dependsOn:[Ljava/lang/String;

    return-object v0
.end method

.method public description()Ljava/lang/String;
    .registers 2

    .line 71
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->description:Ljava/lang/String;

    return-object v0
.end method

.method public message()Ljava/lang/String;
    .registers 2

    .line 85
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->message:Ljava/lang/String;

    return-object v0
.end method

.method public name()Ljava/lang/String;
    .registers 2

    .line 66
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->name:Ljava/lang/String;

    return-object v0
.end method

.method public path()Ljava/lang/String;
    .registers 2

    .line 61
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->path:Ljava/lang/String;

    return-object v0
.end method

.method public size()J
    .registers 3

    .line 90
    iget-wide v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->size:J

    return-wide v0
.end method

.method public state()I
    .registers 2

    .line 80
    iget v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->state:I

    return v0
.end method

.method public type()Lorg/vekendian/nexus/api/ModuleInfo$Type;
    .registers 2

    .line 99
    iget-object v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->type:Lorg/vekendian/nexus/api/ModuleInfo$Type;

    return-object v0
.end method

.method public version()I
    .registers 2

    .line 75
    iget v0, p0, Lorg/vekendian/nexus/api/ModuleInfo;->version:I

    return v0
.end method
