.class Lorg/vekendian/nexus/modules/NexusHost$10;
.super Ljava/lang/Object;
.source "NexusHost.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/modules/NexusHost;->onRemoveClicked(Lorg/vekendian/nexus/api/ModuleInfo;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$s:Lorg/vekendian/nexus/api/ModuleInfo;


# direct methods
.method constructor <init>(Lorg/vekendian/nexus/api/ModuleInfo;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 967
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$10;->val$s:Lorg/vekendian/nexus/api/ModuleInfo;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 3

    .line 969
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$10;->val$s:Lorg/vekendian/nexus/api/ModuleInfo;

    invoke-static {p1}, Lorg/vekendian/nexus/modules/NexusHost;->access$500(Lorg/vekendian/nexus/api/ModuleInfo;)V

    return-void
.end method
