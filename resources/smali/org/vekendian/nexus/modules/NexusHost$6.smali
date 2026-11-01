.class Lorg/vekendian/nexus/modules/NexusHost$6;
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
.field final synthetic val$dialog:[Landroid/app/AlertDialog;


# direct methods
.method constructor <init>([Landroid/app/AlertDialog;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 400
    iput-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$6;->val$dialog:[Landroid/app/AlertDialog;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 3

    .line 402
    iget-object p1, p0, Lorg/vekendian/nexus/modules/NexusHost$6;->val$dialog:[Landroid/app/AlertDialog;

    const/4 v0, 0x0

    aget-object p1, p1, v0

    if-eqz p1, :cond_a

    .line 403
    invoke-virtual {p1}, Landroid/app/AlertDialog;->dismiss()V

    :cond_a
    return-void
.end method
