.class Lorg/vekendian/nexus/modules/NexusHost$3;
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

.field final synthetic val$caps:[Ljava/lang/String;

.field final synthetic val$ui:Landroid/content/Context;


# direct methods
.method constructor <init>([Ljava/lang/String;Landroid/content/Context;[Landroid/widget/Button;[Landroid/widget/Button;)V
    .registers 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 365
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$caps:[Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$ui:Landroid/content/Context;

    iput-object p3, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$allow:[Landroid/widget/Button;

    iput-object p4, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$ask:[Landroid/widget/Button;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 6

    .line 367
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$caps:[Ljava/lang/String;

    array-length v0, p1

    const/4 v1, 0x0

    :goto_4
    if-ge v1, v0, :cond_f

    aget-object v2, p1, v1

    const/4 v3, 0x1

    .line 368
    invoke-static {v2, v3}, Lorg/vekendian/nexus/modules/LuaBridge;->setGlobal(Ljava/lang/String;Z)V

    add-int/lit8 v1, v1, 0x1

    goto :goto_4

    .line 370
    :cond_f
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$ui:Landroid/content/Context;

    iget-object v0, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$caps:[Ljava/lang/String;

    iget-object v1, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$allow:[Landroid/widget/Button;

    iget-object v2, p0, Lorg/vekendian/nexus/modules/NexusHost$3;->val$ask:[Landroid/widget/Button;

    invoke-static {p1, v0, v1, v2}, Lorg/vekendian/nexus/modules/NexusHost;->access$000(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    return-void
.end method
