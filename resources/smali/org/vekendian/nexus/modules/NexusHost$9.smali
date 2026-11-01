.class Lorg/vekendian/nexus/modules/NexusHost$9;
.super Ljava/lang/Object;
.source "NexusHost.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/modules/NexusHost;->rerender()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$a:Landroid/app/Activity;

.field final synthetic val$r:[I


# direct methods
.method constructor <init>(Landroid/app/Activity;[I)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 938
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$9;->val$a:Landroid/app/Activity;

    iput-object p2, p0, Lorg/vekendian/nexus/modules/NexusHost$9;->val$r:[I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .line 940
    iget-object v0, p0, Lorg/vekendian/nexus/modules/NexusHost$9;->val$a:Landroid/app/Activity;

    invoke-static {v0}, Lorg/vekendian/nexus/modules/NexusHost;->access$302(Landroid/app/Activity;)Landroid/app/Activity;

    .line 941
    iget-object v0, p0, Lorg/vekendian/nexus/modules/NexusHost$9;->val$a:Landroid/app/Activity;

    iget-object v1, p0, Lorg/vekendian/nexus/modules/NexusHost$9;->val$r:[I

    invoke-static {v0, v1}, Lorg/vekendian/nexus/modules/NexusHost;->access$400(Landroid/app/Activity;[I)V

    return-void
.end method
