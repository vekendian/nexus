.class final Lorg/vekendian/nexus/modules/ModuleLoader$Meta;
.super Ljava/lang/Object;
.source "ModuleLoader.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lorg/vekendian/nexus/modules/ModuleLoader;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x18
    name = "Meta"
.end annotation


# instance fields
.field autostart:Z

.field description:Ljava/lang/String;

.field name:Ljava/lang/String;

.field version:I


# direct methods
.method constructor <init>()V
    .registers 2

    .line 55
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    const-string v0, ""

    .line 56
    iput-object v0, p0, Lorg/vekendian/nexus/modules/ModuleLoader$Meta;->name:Ljava/lang/String;

    .line 57
    iput-object v0, p0, Lorg/vekendian/nexus/modules/ModuleLoader$Meta;->description:Ljava/lang/String;

    const/4 v0, 0x1

    .line 59
    iput-boolean v0, p0, Lorg/vekendian/nexus/modules/ModuleLoader$Meta;->autostart:Z

    return-void
.end method
