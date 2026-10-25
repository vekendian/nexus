.class Lorg/vekendian/nexus/extensions/NexusToast$2;
.super Ljava/lang/Object;
.source "NexusToast.java"

# interfaces
.implements Landroid/view/View$OnTouchListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lorg/vekendian/nexus/extensions/NexusToast;->present(Landroid/content/Context;Ljava/lang/String;I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field private startTime:J

.field private startY:F

.field final synthetic val$context:Landroid/content/Context;

.field final synthetic val$pill:Landroid/view/View;

.field final synthetic val$wm:Landroid/view/WindowManager;


# direct methods
.method constructor <init>(Landroid/content/Context;Landroid/view/View;Landroid/view/WindowManager;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 90
    iput-object p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$context:Landroid/content/Context;

    iput-object p2, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$pill:Landroid/view/View;

    iput-object p3, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$wm:Landroid/view/WindowManager;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z
    .registers 11

    .line 96
    invoke-virtual {p2}, Landroid/view/MotionEvent;->getAction()I

    move-result v0

    const/4 v1, 0x1

    if-eqz v0, :cond_7d

    const/4 v2, 0x0

    const/16 v3, 0x32

    if-eq v0, v1, :cond_36

    const/4 v4, 0x2

    if-eq v0, v4, :cond_14

    const/4 v4, 0x3

    if-eq v0, v4, :cond_36

    const/4 p1, 0x0

    return p1

    .line 103
    :cond_14
    invoke-virtual {p2}, Landroid/view/MotionEvent;->getRawY()F

    move-result p2

    iget v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->startY:F

    sub-float/2addr p2, v0

    cmpl-float v0, p2, v2

    if-lez v0, :cond_35

    .line 105
    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$context:Landroid/content/Context;

    invoke-static {v0, v3}, Lorg/vekendian/nexus/extensions/NexusToast;->access$100(Landroid/content/Context;I)I

    move-result v0

    int-to-float v0, v0

    iget-object v2, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$context:Landroid/content/Context;

    const/16 v3, 0x64

    invoke-static {v2, v3}, Lorg/vekendian/nexus/extensions/NexusToast;->access$100(Landroid/content/Context;I)I

    move-result v2

    int-to-float v2, v2

    div-float/2addr p2, v2

    mul-float v0, v0, p2

    invoke-virtual {p1, v0}, Landroid/view/View;->setTranslationY(F)V

    :cond_35
    return v1

    .line 111
    :cond_36
    invoke-virtual {p2}, Landroid/view/MotionEvent;->getRawY()F

    move-result p2

    iget v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->startY:F

    sub-float/2addr p2, v0

    .line 112
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    iget-wide v6, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->startTime:J

    sub-long/2addr v4, v6

    .line 113
    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$context:Landroid/content/Context;

    invoke-static {v0, v3}, Lorg/vekendian/nexus/extensions/NexusToast;->access$100(Landroid/content/Context;I)I

    move-result v0

    int-to-float v0, v0

    cmpl-float v0, p2, v0

    if-gtz v0, :cond_75

    iget-object v0, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$context:Landroid/content/Context;

    const/16 v3, 0x14

    invoke-static {v0, v3}, Lorg/vekendian/nexus/extensions/NexusToast;->access$100(Landroid/content/Context;I)I

    move-result v0

    int-to-float v0, v0

    cmpl-float p2, p2, v0

    if-lez p2, :cond_63

    const-wide/16 v6, 0xc8

    cmp-long p2, v4, v6

    if-gez p2, :cond_63

    goto :goto_75

    .line 116
    :cond_63
    invoke-virtual {p1}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object p1

    .line 117
    invoke-virtual {p1, v2}, Landroid/view/ViewPropertyAnimator;->translationY(F)Landroid/view/ViewPropertyAnimator;

    move-result-object p1

    const-wide/16 v2, 0x96

    .line 118
    invoke-virtual {p1, v2, v3}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object p1

    .line 119
    invoke-virtual {p1}, Landroid/view/ViewPropertyAnimator;->start()V

    goto :goto_7c

    .line 114
    :cond_75
    :goto_75
    iget-object p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$pill:Landroid/view/View;

    iget-object p2, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->val$wm:Landroid/view/WindowManager;

    invoke-static {p1, p2}, Lorg/vekendian/nexus/extensions/NexusToast;->access$200(Landroid/view/View;Landroid/view/WindowManager;)V

    :goto_7c
    return v1

    .line 98
    :cond_7d
    invoke-virtual {p2}, Landroid/view/MotionEvent;->getRawY()F

    move-result p1

    iput p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->startY:F

    .line 99
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide p1

    iput-wide p1, p0, Lorg/vekendian/nexus/extensions/NexusToast$2;->startTime:J

    return v1
.end method
