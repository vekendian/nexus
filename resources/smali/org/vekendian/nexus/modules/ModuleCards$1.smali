.class Lorg/vekendian/nexus/modules/ModuleCards$1;
.super Ljava/lang/Object;
.source "ModuleCards.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/modules/ModuleCards;->bind(Landroid/view/LayoutInflater;Landroid/view/ViewGroup;[ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;ILorg/vekendian/nexus/api/ModuleInfo;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$module:Lorg/vekendian/nexus/api/ModuleInfo;


# direct methods
.method constructor <init>(Lorg/vekendian/nexus/api/ModuleInfo;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 57
    iput-object p1, p0, Lorg/vekendian/nexus/modules/ModuleCards$1;->val$module:Lorg/vekendian/nexus/api/ModuleInfo;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 2

    .line 59
    iget-object p1, p0, Lorg/vekendian/nexus/modules/ModuleCards$1;->val$module:Lorg/vekendian/nexus/api/ModuleInfo;

    invoke-static {p1}, Lorg/vekendian/nexus/modules/NexusHost;->onRemoveClicked(Lorg/vekendian/nexus/api/ModuleInfo;)V

    return-void
.end method
