.class Lorg/vekendian/nexus/extensions/NexusToast$3;
.super Ljava/lang/Object;
.source "NexusToast.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/NexusToast;->present(Landroid/content/Context;Ljava/lang/String;I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$pill:Landroid/view/View;

.field final synthetic val$wm:Landroid/view/WindowManager;


# direct methods
.method constructor <init>(Landroid/view/View;Landroid/view/WindowManager;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 129
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$3;->val$pill:Landroid/view/View;

    iput-object p2, p0, Lorg/vekendian/nexus/extensions/NexusToast$3;->val$wm:Landroid/view/WindowManager;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .line 131
    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$3;->val$pill:Landroid/view/View;

    iget-object v1, p0, Lorg/vekendian/nexus/extensions/NexusToast$3;->val$wm:Landroid/view/WindowManager;

    invoke-static {v0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->access$200(Landroid/view/View;Landroid/view/WindowManager;)V

    return-void
.end method
