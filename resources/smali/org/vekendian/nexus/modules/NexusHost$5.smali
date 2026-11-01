.class Lorg/vekendian/nexus/modules/NexusHost$5;
.super Ljava/lang/Object;
.source "NexusHost.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/modules/NexusHost;->permissions(Landroid/content/Context;[I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$r:[I

.field final synthetic val$ui:Landroid/content/Context;


# direct methods
.method constructor <init>(Landroid/content/Context;[I)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 392
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$5;->val$ui:Landroid/content/Context;

    iput-object p2, p0, Lorg/vekendian/nexus/modules/NexusHost$5;->val$r:[I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 4

    .line 394
    invoke-static {}, Lorg/vekendian/nexus/modules/LuaBridge;->clearRemembered()V

    .line 395
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$5;->val$ui:Landroid/content/Context;

    iget-object v0, p0, Lorg/vekendian/nexus/modules/NexusHost$5;->val$r:[I

    const/4 v1, 0x6

    aget v0, v0, v1

    invoke-virtual {p1, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    invoke-static {p1, v0, v1}, Lorg/vekendian/nexus/modules/NexusToast;->show(Landroid/content/Context;Ljava/lang/String;I)V

    return-void
.end method
