.class Lorg/vekendian/nexus/extensions/NexusHost$10;
.super Ljava/lang/Object;
.source "NexusHost.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/NexusHost;->onRemoveClicked(Lorg/vekendian/nexus/api/ExtensionInfo;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$s:Lorg/vekendian/nexus/api/ExtensionInfo;


# direct methods
.method constructor <init>(Lorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 965
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/NexusHost$10;->val$s:Lorg/vekendian/nexus/api/ExtensionInfo;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 3

    .line 967
    iget-object p1, p0, Lorg/vekendian/nexus/extensions/NexusHost$10;->val$s:Lorg/vekendian/nexus/api/ExtensionInfo;

    invoke-static {p1}, Lorg/vekendian/nexus/extensions/NexusHost;->access$500(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    return-void
.end method
