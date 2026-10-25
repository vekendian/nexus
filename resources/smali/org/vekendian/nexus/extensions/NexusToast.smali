.class final Lorg/vekendian/nexus/extensions/NexusToast;
.super Ljava/lang/Object;
.source "NexusToast.java"


# static fields
.field static final ERROR:I = 0x2

.field private static final LONG_MS:J = 0xa28L

.field static final NEUTRAL:I = 0x0

.field static final OK:I = 0x1

.field private static final SHORT_MS:J = 0x640L


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 45
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static synthetic access$000(Landroid/content/Context;Ljava/lang/String;I)V
    .registers 3

    .line 33
    invoke-static {p0, p1, p2}, Lorg/vekendian/nexus/extensions/NexusToast;->present(Landroid/content/Context;Ljava/lang/String;I)V

    return-void
.end method

.method static synthetic access$100(Landroid/content/Context;I)I
    .registers 2

    .line 33
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result p0

    return p0
.end method

.method static synthetic access$200(Landroid/view/View;Landroid/view/WindowManager;)V
    .registers 2

    .line 33
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusToast;->dismissWithAnimation(Landroid/view/View;Landroid/view/WindowManager;)V

    return-void
.end method

.method private static build(Landroid/content/Context;Ljava/lang/String;I)Landroid/view/View;
    .registers 9

    .line 155
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x0

    .line 156
    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v1, 0x10

    .line 157
    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setGravity(I)V

    const-string v2, "nexus_bg_toast"

    const-string v3, "drawable"

    .line 158
    invoke-static {p0, v2, v3}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v2

    if-eqz v2, :cond_1b

    .line 160
    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->setBackgroundResource(I)V

    .line 162
    :cond_1b
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    const/16 v2, 0xc

    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v3

    const/16 v4, 0x14

    invoke-static {p0, v4}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v4

    .line 163
    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v5

    .line 162
    invoke-virtual {v0, v1, v3, v4, v5}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const/16 v1, 0x8

    .line 164
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v3

    int-to-float v3, v3

    invoke-virtual {v0, v3}, Landroid/widget/LinearLayout;->setElevation(F)V

    .line 166
    new-instance v3, Landroid/view/View;

    invoke-direct {v3, p0}, Landroid/view/View;-><init>(Landroid/content/Context;)V

    .line 167
    new-instance v4, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v4}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    const/4 v5, 0x1

    .line 168
    invoke-virtual {v4, v5}, Landroid/graphics/drawable/GradientDrawable;->setShape(I)V

    .line 169
    invoke-static {p0, p2}, Lorg/vekendian/nexus/extensions/NexusToast;->dotColor(Landroid/content/Context;I)I

    move-result p2

    invoke-virtual {v4, p2}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    .line 170
    invoke-virtual {v3, v4}, Landroid/view/View;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 171
    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    .line 172
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v4

    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    invoke-direct {p2, v4, v1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 173
    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    iput v1, p2, Landroid/widget/LinearLayout$LayoutParams;->rightMargin:I

    .line 174
    invoke-virtual {v0, v3, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 176
    new-instance p2, Landroid/widget/TextView;

    invoke-direct {p2, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 177
    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const-string p1, "nexus_text"

    const-string v1, "color"

    .line 178
    invoke-static {p0, p1, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result p1

    if-eqz p1, :cond_7f

    .line 180
    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setTextColor(I)V

    :cond_7f
    const/high16 p1, 0x41600000    # 14.0f

    .line 182
    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setTextSize(F)V

    const/16 p1, 0x118

    .line 183
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result p1

    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setMaxWidth(I)V

    .line 184
    invoke-virtual {v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 186
    new-instance p1, Landroid/widget/FrameLayout;

    invoke-direct {p1, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    .line 187
    invoke-virtual {p1, v0}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;)V

    return-object p1
.end method

.method private static dismissWithAnimation(Landroid/view/View;Landroid/view/WindowManager;)V
    .registers 5

    if-eqz p0, :cond_38

    if-nez p1, :cond_5

    goto :goto_38

    .line 141
    :cond_5
    invoke-virtual {p0}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    .line 142
    invoke-virtual {p0}, Landroid/view/View;->getContext()Landroid/content/Context;

    move-result-object v1

    const/16 v2, 0x64

    invoke-static {v1, v2}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    int-to-float v1, v1

    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->translationY(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const/4 v1, 0x0

    .line 143
    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const-wide/16 v1, 0x96

    .line 144
    invoke-virtual {v0, v1, v2}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    new-instance v1, Landroid/view/animation/AccelerateInterpolator;

    invoke-direct {v1}, Landroid/view/animation/AccelerateInterpolator;-><init>()V

    .line 145
    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    new-instance v1, Lorg/vekendian/nexus/extensions/NexusToast$$ExternalSyntheticLambda0;

    invoke-direct {v1, p1, p0}, Lorg/vekendian/nexus/extensions/NexusToast$$ExternalSyntheticLambda0;-><init>(Landroid/view/WindowManager;Landroid/view/View;)V

    .line 146
    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->withEndAction(Ljava/lang/Runnable;)Landroid/view/ViewPropertyAnimator;

    move-result-object p0

    .line 151
    invoke-virtual {p0}, Landroid/view/ViewPropertyAnimator;->start()V

    :cond_38
    :goto_38
    return-void
.end method

.method private static dotColor(Landroid/content/Context;I)I
    .registers 6

    const/4 v0, 0x2

    const/4 v1, 0x1

    if-ne p1, v1, :cond_7

    const-string v2, "nexus_ok"

    goto :goto_e

    :cond_7
    if-ne p1, v0, :cond_c

    const-string v2, "nexus_bad"

    goto :goto_e

    :cond_c
    const-string v2, "nexus_orange"

    :goto_e
    const-string v3, "color"

    .line 200
    invoke-static {p0, v2, v3}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v2

    if-eqz v2, :cond_20

    .line 203
    :try_start_16
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object p0

    invoke-virtual {p0, v2}, Landroid/content/res/Resources;->getColor(I)I

    move-result p0
    :try_end_1e
    .catchall {:try_start_16 .. :try_end_1e} :catchall_1f

    return p0

    :catchall_1f
    nop

    :cond_20
    if-ne p1, v1, :cond_26

    const p0, -0xb52180

    goto :goto_2f

    :cond_26
    if-ne p1, v0, :cond_2c

    const p0, -0xa3a4

    goto :goto_2f

    :cond_2c
    const p0, -0x8600

    :goto_2f
    return p0
.end method

.method private static dp(Landroid/content/Context;I)I
    .registers 2

    int-to-float p1, p1

    .line 219
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object p0

    invoke-virtual {p0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object p0

    iget p0, p0, Landroid/util/DisplayMetrics;->density:F

    mul-float p1, p1, p0

    const/high16 p0, 0x3f000000    # 0.5f

    add-float/2addr p1, p0

    float-to-int p0, p1

    return p0
.end method

.method static synthetic lambda$dismissWithAnimation$0(Landroid/view/WindowManager;Landroid/view/View;)V
    .registers 2

    .line 148
    :try_start_0
    invoke-interface {p0, p1}, Landroid/view/WindowManager;->removeView(Landroid/view/View;)V
    :try_end_3
    .catchall {:try_start_0 .. :try_end_3} :catchall_3

    :catchall_3
    return-void
.end method

.method private static overlayType()I
    .registers 2

    .line 212
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1a

    if-lt v0, v1, :cond_9

    const/16 v0, 0x7f6

    return v0

    :cond_9
    const/16 v0, 0x7d2

    return v0
.end method

.method private static present(Landroid/content/Context;Ljava/lang/String;I)V
    .registers 11

    :try_start_0
    const-string v0, "window"

    .line 62
    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/view/WindowManager;

    if-nez v0, :cond_b

    return-void

    .line 67
    :cond_b
    invoke-static {p0, p1, p2}, Lorg/vekendian/nexus/extensions/NexusToast;->build(Landroid/content/Context;Ljava/lang/String;I)Landroid/view/View;

    move-result-object p1

    .line 68
    new-instance v7, Landroid/view/WindowManager$LayoutParams;

    const/4 v2, -0x2

    const/4 v3, -0x2

    .line 71
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusToast;->overlayType()I

    move-result v4

    const/16 v5, 0x18

    const/4 v6, -0x3

    move-object v1, v7

    invoke-direct/range {v1 .. v6}, Landroid/view/WindowManager$LayoutParams;-><init>(IIIII)V

    const/16 v1, 0x51

    .line 75
    iput v1, v7, Landroid/view/WindowManager$LayoutParams;->gravity:I

    const/16 v1, 0x68

    .line 76
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    neg-int v1, v1

    iput v1, v7, Landroid/view/WindowManager$LayoutParams;->y:I

    .line 77
    invoke-interface {v0, p1, v7}, Landroid/view/WindowManager;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const/16 v1, 0x64

    .line 80
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusToast;->dp(Landroid/content/Context;I)I

    move-result v1

    int-to-float v1, v1

    invoke-virtual {p1, v1}, Landroid/view/View;->setTranslationY(F)V

    const/4 v1, 0x0

    .line 81
    invoke-virtual {p1, v1}, Landroid/view/View;->setAlpha(F)V

    .line 82
    invoke-virtual {p1}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object v2

    .line 83
    invoke-virtual {v2, v1}, Landroid/view/ViewPropertyAnimator;->translationY(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v1

    const/high16 v2, 0x3f800000    # 1.0f

    .line 84
    invoke-virtual {v1, v2}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v1

    const-wide/16 v2, 0xc8

    .line 85
    invoke-virtual {v1, v2, v3}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object v1

    new-instance v2, Landroid/view/animation/DecelerateInterpolator;

    invoke-direct {v2}, Landroid/view/animation/DecelerateInterpolator;-><init>()V

    .line 86
    invoke-virtual {v1, v2}, Landroid/view/ViewPropertyAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)Landroid/view/ViewPropertyAnimator;

    move-result-object v1

    .line 87
    invoke-virtual {v1}, Landroid/view/ViewPropertyAnimator;->start()V

    .line 90
    new-instance v1, Lorg/vekendian/nexus/extensions/NexusToast$2;

    invoke-direct {v1, p0, p1, v0}, Lorg/vekendian/nexus/extensions/NexusToast$2;-><init>(Landroid/content/Context;Landroid/view/View;Landroid/view/WindowManager;)V

    invoke-virtual {p1, v1}, Landroid/view/View;->setOnTouchListener(Landroid/view/View$OnTouchListener;)V

    .line 128
    new-instance p0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {p0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    .line 129
    new-instance v1, Lorg/vekendian/nexus/extensions/NexusToast$3;

    invoke-direct {v1, p1, v0}, Lorg/vekendian/nexus/extensions/NexusToast$3;-><init>(Landroid/view/View;Landroid/view/WindowManager;)V

    if-nez p2, :cond_77

    const-wide/16 p1, 0x640

    goto :goto_79

    :cond_77
    const-wide/16 p1, 0xa28

    :goto_79
    invoke-virtual {p0, v1, p1, p2}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z
    :try_end_7c
    .catchall {:try_start_0 .. :try_end_7c} :catchall_7d

    goto :goto_96

    :catchall_7d
    move-exception p0

    .line 135
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "toast failed: "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :goto_96
    return-void
.end method

.method static show(Landroid/content/Context;Ljava/lang/String;I)V
    .registers 5

    if-eqz p0, :cond_26

    if-eqz p1, :cond_26

    .line 49
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v0

    if-nez v0, :cond_b

    goto :goto_26

    .line 52
    :cond_b
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_15

    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object p0

    .line 53
    :cond_15
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    new-instance v1, Lorg/vekendian/nexus/extensions/NexusToast$1;

    invoke-direct {v1, p0, p1, p2}, Lorg/vekendian/nexus/extensions/NexusToast$1;-><init>(Landroid/content/Context;Ljava/lang/String;I)V

    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    :cond_26
    :goto_26
    return-void
.end method
