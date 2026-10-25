.class Lorg/vekendian/nexus/extensions/NexusToast$1;
.super Ljava/lang/Object;
.source "NexusToast.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/NexusToast;->show(Landroid/content/Context;Ljava/lang/String;I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$app:Landroid/content/Context;

.field final synthetic val$kind:I

.field final synthetic val$message:Ljava/lang/String;


# direct methods
.method constructor <init>(Landroid/content/Context;Ljava/lang/String;I)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 53
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$app:Landroid/content/Context;

    iput-object p2, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$message:Ljava/lang/String;

    iput p3, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$kind:I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 4

    .line 55
    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$app:Landroid/content/Context;

    iget-object v1, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$message:Ljava/lang/String;

    iget v2, p0, Lorg/vekendian/nexus/extensions/NexusToast$1;->val$kind:I

    invoke-static {v0, v1, v2}, Lorg/vekendian/nexus/extensions/NexusToast;->access$000(Landroid/content/Context;Ljava/lang/String;I)V

    return-void
.end method
