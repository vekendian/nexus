.class Lorg/vekendian/nexus/extensions/NexusHost$7;
.super Ljava/lang/Object;
.source "NexusHost.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/NexusHost;->importUri(Landroid/net/Uri;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$uri:Landroid/net/Uri;


# direct methods
.method constructor <init>(Landroid/net/Uri;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 687
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/NexusHost$7;->val$uri:Landroid/net/Uri;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .line 689
    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusHost$7;->val$uri:Landroid/net/Uri;

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->access$100(Landroid/net/Uri;)V

    return-void
.end method
