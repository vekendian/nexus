.class public Landroid/ext/r$ModuleRemove;
.super Ljava/lang/Object;
.source "NexusModuleRemove.java"

# implements Landroid/view/View$OnClickListener
.implements Landroid/view/View$OnClickListener;

# instance fields
.field final synthetic this$0:Landroid/ext/r;
.field private final uri:Ljava/lang/String;

# direct methods
.method constructor <init>(Landroid/ext/r;Ljava/lang/String;)V
    .registers 3
    iput-object p1, p0, Landroid/ext/r$ModuleRemove;->this$0:Landroid/ext/r;
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p2, p0, Landroid/ext/r$ModuleRemove;->uri:Ljava/lang/String;
    return-void
.end method

# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 4
    iget-object v0, p0, Landroid/ext/r$ModuleRemove;->this$0:Landroid/ext/r;
    iget-object v1, p0, Landroid/ext/r$ModuleRemove;->uri:Ljava/lang/String;
    if-eqz v0, :mr_done
    if-eqz v1, :mr_done
    invoke-direct {v0, v1}, Landroid/ext/r;->nexusModulesRemove(Ljava/lang/String;)V
    :mr_done
    return-void
.end method
