.class Lorg/vekendian/nexus/extensions/ExtensionCards$1;
.super Ljava/lang/Object;
.source "ExtensionCards.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/ExtensionCards;->bind(Landroid/view/LayoutInflater;Landroid/view/ViewGroup;[ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;ILorg/vekendian/nexus/api/ExtensionInfo;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$extension:Lorg/vekendian/nexus/api/ExtensionInfo;


# direct methods
.method constructor <init>(Lorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 57
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/ExtensionCards$1;->val$extension:Lorg/vekendian/nexus/api/ExtensionInfo;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 2

    .line 59
    iget-object p1, p0, Lorg/vekendian/nexus/extensions/ExtensionCards$1;->val$extension:Lorg/vekendian/nexus/api/ExtensionInfo;

    invoke-static {p1}, Lorg/vekendian/nexus/extensions/NexusHost;->onRemoveClicked(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    return-void
.end method
