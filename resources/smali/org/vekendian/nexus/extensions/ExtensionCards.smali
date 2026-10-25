.class final Lorg/vekendian/nexus/extensions/ExtensionCards;
.super Ljava/lang/Object;
.source "ExtensionCards.java"


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 21
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static bind(Landroid/view/LayoutInflater;Landroid/view/ViewGroup;[ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;ILorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 10

    const/4 v0, 0x2

    .line 29
    :try_start_1
    aget v0, p2, v0

    const/4 v1, 0x0

    invoke-virtual {p0, v0, p1, v1}, Landroid/view/LayoutInflater;->inflate(ILandroid/view/ViewGroup;Z)Landroid/view/View;

    move-result-object p0
    :try_end_8
    .catchall {:try_start_1 .. :try_end_8} :catchall_41

    if-nez p0, :cond_b

    return-void

    .line 42
    :cond_b
    invoke-virtual {p1, p0}, Landroid/view/ViewGroup;->addView(Landroid/view/View;)V

    const/4 p1, 0x3

    .line 43
    aget p1, p2, p1

    invoke-static {p0, p1, p3}, Lorg/vekendian/nexus/extensions/ExtensionCards;->setText(Landroid/view/View;ILjava/lang/String;)V

    const/4 p1, 0x4

    .line 44
    aget p1, p2, p1

    invoke-static {p0, p1, p4}, Lorg/vekendian/nexus/extensions/ExtensionCards;->setText(Landroid/view/View;ILjava/lang/String;)V

    const/4 p1, 0x5

    .line 45
    aget p3, p2, p1

    invoke-static {p0, p3, p5}, Lorg/vekendian/nexus/extensions/ExtensionCards;->setText(Landroid/view/View;ILjava/lang/String;)V

    .line 46
    aget p1, p2, p1

    invoke-static {p0, p1, p6}, Lorg/vekendian/nexus/extensions/ExtensionCards;->setColor(Landroid/view/View;II)V

    const/4 p1, 0x6

    .line 48
    aget p1, p2, p1

    invoke-virtual {p0, p1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object p0

    if-nez p7, :cond_36

    if-eqz p0, :cond_35

    const/16 p1, 0x8

    .line 52
    invoke-virtual {p0, p1}, Landroid/view/View;->setVisibility(I)V

    :cond_35
    return-void

    :cond_36
    if-eqz p0, :cond_40

    .line 57
    new-instance p1, Lorg/vekendian/nexus/extensions/ExtensionCards$1;

    invoke-direct {p1, p7}, Lorg/vekendian/nexus/extensions/ExtensionCards$1;-><init>(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    invoke-virtual {p0, p1}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    :cond_40
    return-void

    :catchall_41
    move-exception p0

    .line 31
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "card inflate failed: "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    return-void
.end method

.method private static setColor(Landroid/view/View;II)V
    .registers 3

    if-eqz p1, :cond_12

    if-nez p2, :cond_5

    goto :goto_12

    .line 85
    :cond_5
    invoke-virtual {p0, p1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object p0

    .line 86
    instance-of p1, p0, Landroid/widget/TextView;

    if-eqz p1, :cond_12

    .line 87
    check-cast p0, Landroid/widget/TextView;

    invoke-virtual {p0, p2}, Landroid/widget/TextView;->setTextColor(I)V

    :cond_12
    :goto_12
    return-void
.end method

.method private static setText(Landroid/view/View;ILjava/lang/String;)V
    .registers 3

    if-eqz p1, :cond_12

    if-nez p2, :cond_5

    goto :goto_12

    .line 69
    :cond_5
    invoke-virtual {p0, p1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object p0

    .line 70
    instance-of p1, p0, Landroid/widget/TextView;

    if-eqz p1, :cond_12

    .line 71
    check-cast p0, Landroid/widget/TextView;

    invoke-virtual {p0, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_12
    :goto_12
    return-void
.end method
