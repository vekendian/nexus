.class Lorg/vekendian/nexus/modules/NexusHost$2;
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
.field final synthetic val$allow:[Landroid/widget/Button;

.field final synthetic val$ask:[Landroid/widget/Button;

.field final synthetic val$cap:Ljava/lang/String;

.field final synthetic val$caps:[Ljava/lang/String;

.field final synthetic val$ui:Landroid/content/Context;


# direct methods
.method constructor <init>(Ljava/lang/String;Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V
    .registers 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 349
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$cap:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$ui:Landroid/content/Context;

    iput-object p3, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$caps:[Ljava/lang/String;

    iput-object p4, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$allow:[Landroid/widget/Button;

    iput-object p5, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$ask:[Landroid/widget/Button;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 5

    .line 351
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$cap:Ljava/lang/String;

    const/4 v0, 0x0

    invoke-static {p1, v0}, Lorg/vekendian/nexus/modules/LuaBridge;->setGlobal(Ljava/lang/String;Z)V

    .line 352
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$ui:Landroid/content/Context;

    iget-object v0, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$caps:[Ljava/lang/String;

    iget-object v1, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$allow:[Landroid/widget/Button;

    iget-object v2, p0, Lorg/vekendian/nexus/modules/NexusHost$2;->val$ask:[Landroid/widget/Button;

    invoke-static {p1, v0, v1, v2}, Lorg/vekendian/nexus/modules/NexusHost;->access$000(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    return-void
.end method
