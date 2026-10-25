.class public final Lorg/vekendian/nexus/extensions/NexusHost;
.super Ljava/lang/Object;
.source "NexusHost.java"


# static fields
.field private static final EXTENSIONS_DIR:Ljava/lang/String; = "extensions"

.field private static final I_CARD:I = 0x2

.field private static final I_DESC:I = 0x5

.field private static final I_EMPTY:I = 0x1

.field private static final I_ERROR:I = 0xd

.field private static final I_EXEC:I = 0x7

.field private static final I_FIN:I = 0xb

.field private static final I_IDLE:I = 0x9

.field private static final I_LIST:I = 0x0

.field private static final I_LOADED:I = 0x8

.field private static final I_META:I = 0x4

.field private static final I_REMOVE:I = 0x6

.field private static final I_REMOVE_MSG:I = 0xf

.field private static final I_REMOVE_TITLE:I = 0xe

.field private static final I_RUN:I = 0xa

.field private static final I_STOP:I = 0xc

.field private static final I_TITLE:I = 0x3

.field private static final PICKER_CLASS:Ljava/lang/String; = "org.vekendian.nexus.ModulePicker"

.field private static final PICK_MIME:[Ljava/lang/String;

.field public static final TAG:Ljava/lang/String; = "NexusMod"

.field private static activity:Landroid/app/Activity;

.field private static api:Lorg/vekendian/nexus/extensions/ExtensionApiImpl;

.field private static app:Landroid/content/Context;

.field private static executor:Lorg/vekendian/nexus/api/NexusExecutor;

.field private static failure:Ljava/lang/String;

.field private static ids:[I

.field private static module:Ljava/lang/Object;

.field private static moduleName:Ljava/lang/String;

.field private static moduleVersion:I

.field private static volatile pending:Landroid/net/Uri;

.field private static rawId:I


# direct methods
.method static constructor <clinit>()V
    .registers 4

    const-string v0, "application/octet-stream"

    const-string v1, "application/vnd.android.dex-archive"

    const-string v2, "application/java-archive"

    const-string v3, "text/plain"

    .line 72
    filled-new-array {v0, v1, v2, v3}, [Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->PICK_MIME:[Ljava/lang/String;

    const-string v0, ""

    .line 96
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->moduleName:Ljava/lang/String;

    return-void
.end method

.method private constructor <init>()V
    .registers 1

    .line 100
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static synthetic access$000(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V
    .registers 4

    .line 54
    invoke-static {p0, p1, p2, p3}, Lorg/vekendian/nexus/extensions/NexusHost;->syncPermissionButtons(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    return-void
.end method

.method static synthetic access$100(Landroid/net/Uri;)V
    .registers 1

    .line 54
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->importUriNow(Landroid/net/Uri;)V

    return-void
.end method

.method static synthetic access$200()Landroid/content/Context;
    .registers 1

    .line 54
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    return-object v0
.end method

.method static synthetic access$302(Landroid/app/Activity;)Landroid/app/Activity;
    .registers 1

    .line 54
    sput-object p0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    return-object p0
.end method

.method static synthetic access$400(Landroid/app/Activity;[I)V
    .registers 2

    .line 54
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusHost;->draw(Landroid/app/Activity;[I)V

    return-void
.end method

.method static synthetic access$500(Lorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 1

    .line 54
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->removeExtension(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    return-void
.end method

.method static activity()Landroid/app/Activity;
    .registers 1

    .line 255
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    return-object v0
.end method

.method static app()Landroid/content/Context;
    .registers 1

    .line 251
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    return-object v0
.end method

.method public static boot(Landroid/app/Activity;I)V
    .registers 3

    if-nez p0, :cond_3

    return-void

    .line 168
    :cond_3
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    if-nez v0, :cond_14

    .line 169
    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    .line 170
    new-instance v0, Lorg/vekendian/nexus/extensions/ExtensionApiImpl;

    invoke-direct {v0}, Lorg/vekendian/nexus/extensions/ExtensionApiImpl;-><init>()V

    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->api:Lorg/vekendian/nexus/extensions/ExtensionApiImpl;

    .line 172
    :cond_14
    sput-object p0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    .line 173
    sput p1, Lorg/vekendian/nexus/extensions/NexusHost;->rawId:I

    .line 174
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->ensureExecutor()V

    .line 176
    sget-object p0, Lorg/vekendian/nexus/extensions/NexusHost;->pending:Landroid/net/Uri;

    if-eqz p0, :cond_25

    const/4 p1, 0x0

    .line 180
    sput-object p1, Lorg/vekendian/nexus/extensions/NexusHost;->pending:Landroid/net/Uri;

    .line 181
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->importUri(Landroid/net/Uri;)V

    .line 183
    :cond_25
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->powerOn()V

    return-void
.end method

.method private static color(Landroid/content/Context;Ljava/lang/String;)I
    .registers 3

    const-string v0, "color"

    .line 553
    invoke-static {p0, p1, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result p0

    return p0
.end method

.method private static colorValue(Landroid/content/Context;Ljava/lang/String;I)I
    .registers 3

    .line 565
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p1

    if-nez p1, :cond_7

    return p2

    .line 570
    :cond_7
    :try_start_7
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object p0

    invoke-virtual {p0, p1}, Landroid/content/res/Resources;->getColor(I)I

    move-result p0
    :try_end_f
    .catchall {:try_start_7 .. :try_end_f} :catchall_10

    return p0

    :catchall_10
    return p2
.end method

.method public static dialogBuilder()Landroid/app/AlertDialog$Builder;
    .registers 2

    .line 449
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->dialogContext()Landroid/content/Context;

    move-result-object v0

    if-nez v0, :cond_8

    const/4 v0, 0x0

    goto :goto_e

    .line 450
    :cond_8
    new-instance v1, Landroid/app/AlertDialog$Builder;

    invoke-direct {v1, v0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    move-object v0, v1

    :goto_e
    return-object v0
.end method

.method public static dialogBuilder(Landroid/content/Context;)Landroid/app/AlertDialog$Builder;
    .registers 2

    if-nez p0, :cond_4

    const/4 p0, 0x0

    goto :goto_e

    .line 461
    :cond_4
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->themedContext(Landroid/content/Context;)Landroid/content/Context;

    move-result-object p0

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    move-object p0, v0

    :goto_e
    return-object p0
.end method

.method private static dialogContext()Landroid/content/Context;
    .registers 1

    .line 431
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    if-eqz v0, :cond_5

    goto :goto_7

    :cond_5
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    :goto_7
    if-nez v0, :cond_b

    const/4 v0, 0x0

    goto :goto_f

    .line 432
    :cond_b
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->themedContext(Landroid/content/Context;)Landroid/content/Context;

    move-result-object v0

    :goto_f
    return-object v0
.end method

.method private static dp(Landroid/content/Context;I)I
    .registers 2

    int-to-float p1, p1

    .line 669
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

.method private static draw(Landroid/app/Activity;[I)V
    .registers 16

    const/4 v0, 0x0

    .line 794
    aget v1, p1, v0

    invoke-virtual {p0, v1}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;

    move-result-object v1

    .line 795
    instance-of v2, v1, Landroid/view/ViewGroup;

    if-nez v2, :cond_c

    return-void

    .line 798
    :cond_c
    check-cast v1, Landroid/view/ViewGroup;

    .line 799
    invoke-virtual {v1}, Landroid/view/ViewGroup;->removeAllViews()V

    .line 800
    invoke-static {p0}, Landroid/view/LayoutInflater;->from(Landroid/content/Context;)Landroid/view/LayoutInflater;

    move-result-object v2

    .line 802
    sget-object v3, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    const/16 v11, 0x8

    if-nez v3, :cond_21

    aget v3, p1, v11

    invoke-virtual {p0, v3}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object v3

    :cond_21
    move-object v8, v3

    const/4 v3, 0x7

    .line 803
    aget v3, p1, v3

    .line 804
    invoke-virtual {p0, v3}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object v6

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "nexus_dexexec \u00b7 Nexus "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 805
    sget-object v4, Lorg/vekendian/nexus/extensions/NexusHost;->api:Lorg/vekendian/nexus/extensions/ExtensionApiImpl;

    if-nez v4, :cond_3a

    const-string v4, "?"

    goto :goto_3e

    :cond_3a
    invoke-virtual {v4}, Lorg/vekendian/nexus/extensions/ExtensionApiImpl;->appVersion()Ljava/lang/String;

    move-result-object v4

    :goto_3e
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v4, " \u00b7 v"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget v4, Lorg/vekendian/nexus/extensions/NexusHost;->moduleVersion:I

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v7

    const/4 v9, 0x0

    const/4 v10, 0x0

    move-object v3, v2

    move-object v4, v1

    move-object v5, p1

    .line 803
    invoke-static/range {v3 .. v10}, Lorg/vekendian/nexus/extensions/ExtensionCards;->bind(Landroid/view/LayoutInflater;Landroid/view/ViewGroup;[ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;ILorg/vekendian/nexus/api/ExtensionInfo;)V

    const/4 v3, 0x0

    .line 811
    sget-object v4, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-eqz v4, :cond_7a

    .line 813
    :try_start_5c
    invoke-interface {v4}, Lorg/vekendian/nexus/api/NexusExecutor;->extensions()Ljava/util/List;

    move-result-object v3
    :try_end_60
    .catchall {:try_start_5c .. :try_end_60} :catchall_61

    goto :goto_7a

    :catchall_61
    move-exception v4

    .line 815
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "extensions() failed: "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v4}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :cond_7a
    :goto_7a
    if-eqz v3, :cond_a8

    .line 819
    invoke-interface {v3}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v12

    const/4 v3, 0x0

    :goto_81
    invoke-interface {v12}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_a9

    invoke-interface {v12}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    move-object v10, v4

    check-cast v10, Lorg/vekendian/nexus/api/ExtensionInfo;

    add-int/lit8 v13, v3, 0x1

    .line 821
    invoke-virtual {v10}, Lorg/vekendian/nexus/api/ExtensionInfo;->name()Ljava/lang/String;

    move-result-object v6

    .line 822
    invoke-static {p0, v10}, Lorg/vekendian/nexus/extensions/NexusHost;->extensionMeta(Landroid/content/Context;Lorg/vekendian/nexus/api/ExtensionInfo;)Ljava/lang/String;

    move-result-object v7

    invoke-static {p0, p1, v10}, Lorg/vekendian/nexus/extensions/NexusHost;->extensionDesc(Landroid/app/Activity;[ILorg/vekendian/nexus/api/ExtensionInfo;)Ljava/lang/String;

    move-result-object v8

    .line 823
    invoke-static {p0, v10}, Lorg/vekendian/nexus/extensions/NexusHost;->statusColor(Landroid/content/Context;Lorg/vekendian/nexus/api/ExtensionInfo;)I

    move-result v9

    move-object v3, v2

    move-object v4, v1

    move-object v5, p1

    .line 821
    invoke-static/range {v3 .. v10}, Lorg/vekendian/nexus/extensions/ExtensionCards;->bind(Landroid/view/LayoutInflater;Landroid/view/ViewGroup;[ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;ILorg/vekendian/nexus/api/ExtensionInfo;)V

    move v3, v13

    goto :goto_81

    :cond_a8
    const/4 v3, 0x0

    :cond_a9
    const/4 v1, 0x1

    .line 828
    aget p1, p1, v1

    invoke-virtual {p0, p1}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;

    move-result-object p0

    if-eqz p0, :cond_ba

    if-nez v3, :cond_b5

    goto :goto_b7

    :cond_b5
    const/16 v0, 0x8

    .line 830
    :goto_b7
    invoke-virtual {p0, v0}, Landroid/view/View;->setVisibility(I)V

    :cond_ba
    return-void
.end method

.method private static ensureExecutor()V
    .registers 6

    .line 759
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-nez v0, :cond_95

    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    if-eqz v0, :cond_a

    goto/16 :goto_95

    .line 762
    :cond_a
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    if-eqz v0, :cond_95

    sget v1, Lorg/vekendian/nexus/extensions/NexusHost;->rawId:I

    if-nez v1, :cond_14

    goto/16 :goto_95

    .line 765
    :cond_14
    invoke-static {v0, v1}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->extract(Landroid/content/Context;I)Ljava/io/File;

    move-result-object v0

    if-nez v0, :cond_1f

    const-string v0, "executor asset unavailable"

    .line 767
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    return-void

    .line 770
    :cond_1f
    new-instance v1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;

    invoke-direct {v1}, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;-><init>()V

    const/4 v2, 0x1

    new-array v3, v2, [Ljava/lang/String;

    .line 772
    sget-object v4, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    const-class v5, Lorg/vekendian/nexus/extensions/NexusHost;

    invoke-virtual {v5}, Ljava/lang/Class;->getClassLoader()Ljava/lang/ClassLoader;

    move-result-object v5

    invoke-static {v4, v5, v0, v1, v3}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->load(Landroid/content/Context;Ljava/lang/ClassLoader;Ljava/io/File;Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;[Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    const/4 v4, 0x0

    if-nez v0, :cond_3b

    aget-object v0, v3, v4

    .line 774
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    return-void

    .line 777
    :cond_3b
    instance-of v5, v0, Lorg/vekendian/nexus/api/NexusExecutor;

    if-nez v5, :cond_44

    const-string v0, "entry class does not implement NexusExecutor"

    .line 778
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    return-void

    .line 781
    :cond_44
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->module:Ljava/lang/Object;

    .line 782
    move-object v5, v0

    check-cast v5, Lorg/vekendian/nexus/api/NexusExecutor;

    sput-object v5, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    .line 783
    iget-object v5, v1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->name:Ljava/lang/String;

    invoke-virtual {v5}, Ljava/lang/String;->length()I

    move-result v5

    if-nez v5, :cond_56

    const-string v5, "Nexus extension"

    goto :goto_58

    :cond_56
    iget-object v5, v1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->name:Ljava/lang/String;

    :goto_58
    sput-object v5, Lorg/vekendian/nexus/extensions/NexusHost;->moduleName:Ljava/lang/String;

    .line 784
    iget v1, v1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->version:I

    sput v1, Lorg/vekendian/nexus/extensions/NexusHost;->moduleVersion:I

    new-array v1, v2, [Ljava/lang/Class;

    .line 785
    const-class v5, Lorg/vekendian/nexus/api/ExtensionApi;

    aput-object v5, v1, v4

    new-array v2, v2, [Ljava/lang/Object;

    sget-object v5, Lorg/vekendian/nexus/extensions/NexusHost;->api:Lorg/vekendian/nexus/extensions/ExtensionApiImpl;

    aput-object v5, v2, v4

    const-string v5, "onLoad"

    invoke-static {v0, v5, v1, v2, v3}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->call(Ljava/lang/Object;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;[Ljava/lang/String;)V

    aget-object v0, v3, v4

    if-eqz v0, :cond_75

    .line 788
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    .line 790
    :cond_75
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "Extension Registry loaded: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->moduleName:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, " v"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget v1, Lorg/vekendian/nexus/extensions/NexusHost;->moduleVersion:I

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :cond_95
    :goto_95
    return-void
.end method

.method public static executor()Lorg/vekendian/nexus/api/NexusExecutor;
    .registers 1

    .line 265
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    return-object v0
.end method

.method private static extensionDesc(Landroid/app/Activity;[ILorg/vekendian/nexus/api/ExtensionInfo;)Ljava/lang/String;
    .registers 5

    .line 891
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v0

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    if-eq v0, v1, :cond_77

    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v0

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    if-ne v0, v1, :cond_11

    goto :goto_77

    .line 894
    :cond_11
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->state()I

    move-result v0

    const/4 v1, 0x1

    if-eq v0, v1, :cond_6e

    const/4 v1, 0x2

    if-eq v0, v1, :cond_65

    const/4 v1, 0x3

    if-eq v0, v1, :cond_5c

    const/4 v1, 0x4

    if-eq v0, v1, :cond_40

    .line 906
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->description()Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_37

    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->description()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v0

    if-nez v0, :cond_32

    goto :goto_37

    .line 907
    :cond_32
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->description()Ljava/lang/String;

    move-result-object p0

    goto :goto_3f

    :cond_37
    :goto_37
    const/16 p2, 0x9

    aget p1, p1, p2

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    :goto_3f
    return-object p0

    :cond_40
    const/16 v0, 0xd

    .line 902
    aget p1, p1, v0

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    .line 903
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->message()Ljava/lang/String;

    move-result-object p1

    if-nez p1, :cond_51

    const-string p1, "?"

    goto :goto_55

    :cond_51
    invoke-virtual {p2}, Lorg/vekendian/nexus/api/ExtensionInfo;->message()Ljava/lang/String;

    move-result-object p1

    :goto_55
    const-string p2, "%s"

    .line 902
    invoke-virtual {p0, p2, p1}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_5c
    const/16 p2, 0xc

    .line 900
    aget p1, p1, p2

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_65
    const/16 p2, 0xb

    .line 898
    aget p1, p1, p2

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_6e
    const/16 p2, 0xa

    .line 896
    aget p1, p1, p2

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_77
    :goto_77
    const/16 p2, 0x8

    .line 892
    aget p1, p1, p2

    invoke-virtual {p0, p1}, Landroid/app/Activity;->getString(I)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method private static extensionMeta(Landroid/content/Context;Lorg/vekendian/nexus/api/ExtensionInfo;)Ljava/lang/String;
    .registers 10

    .line 842
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_9

    const-string v0, ""

    goto :goto_d

    :cond_9
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v0

    .line 843
    :goto_d
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->extensionsDir()Ljava/lang/String;

    move-result-object v1

    .line 845
    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_20

    .line 846
    invoke-virtual {v1}, Ljava/lang/String;->length()I

    move-result v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    goto :goto_21

    :cond_20
    move-object v1, v0

    :goto_21
    const-string v2, "/"

    .line 848
    invoke-virtual {v1, v2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v2

    const/4 v3, 0x1

    if-eqz v2, :cond_2f

    .line 849
    invoke-virtual {v1, v3}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    goto :goto_21

    .line 851
    :cond_2f
    invoke-virtual {v1}, Ljava/lang/String;->length()I

    move-result v2

    if-nez v2, :cond_3e

    .line 852
    new-instance v1, Ljava/io/File;

    invoke-direct {v1, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v1

    .line 854
    :cond_3e
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v1, Ljava/util/Locale;->US:Ljava/util/Locale;

    new-array v2, v3, [Ljava/lang/Object;

    const/4 v3, 0x0

    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->size()J

    move-result-wide v4

    long-to-double v4, v4

    const-wide/high16 v6, 0x4090000000000000L    # 1024.0

    div-double/2addr v4, v6

    invoke-static {v4, v5}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v4

    aput-object v4, v2, v3

    const-string v3, " \u00b7 %.1f KB"

    invoke-static {v1, v3, v2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 855
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->autostart()Z

    move-result v1

    const-string v2, " \u00b7 "

    if-eqz v1, :cond_88

    .line 856
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, "nexus_str_extension_autostart"

    const-string v3, "autostart"

    invoke-static {p0, v0, v3}, Lorg/vekendian/nexus/extensions/NexusHost;->text(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 859
    :cond_88
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v1

    sget-object v3, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    if-eq v1, v3, :cond_98

    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object p1

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    if-ne p1, v1, :cond_b2

    .line 860
    :cond_98
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, "nexus_str_extension_jar"

    const-string v1, "JAR"

    invoke-static {p0, v0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->text(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :cond_b2
    return-object v0
.end method

.method static extensionsDir()Ljava/lang/String;
    .registers 3

    .line 673
    new-instance v0, Ljava/io/File;

    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    invoke-virtual {v1}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v1

    const-string v2, "extensions"

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method private static footerParams(Landroid/content/Context;)Landroid/widget/LinearLayout$LayoutParams;
    .registers 5

    .line 662
    new-instance v0, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v1, 0x0

    const/4 v2, -0x2

    const/high16 v3, 0x3f800000    # 1.0f

    invoke-direct {v0, v1, v2, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    const/4 v2, 0x4

    .line 664
    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v3

    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result p0

    invoke-virtual {v0, v3, v1, p0, v1}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    return-object v0
.end method

.method private static importFailed(Ljava/lang/String;)V
    .registers 3

    .line 740
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "import failed: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    .line 741
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    if-eqz v0, :cond_25

    .line 742
    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    if-nez v1, :cond_1d

    goto :goto_25

    .line 745
    :cond_1d
    new-instance v1, Lorg/vekendian/nexus/extensions/NexusHost$8;

    invoke-direct {v1, p0}, Lorg/vekendian/nexus/extensions/NexusHost$8;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, v1}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    :cond_25
    :goto_25
    return-void
.end method

.method private static importUri(Landroid/net/Uri;)V
    .registers 3

    .line 681
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-nez v0, :cond_e

    .line 682
    sget-object p0, Lorg/vekendian/nexus/extensions/NexusHost;->failure:Ljava/lang/String;

    if-nez p0, :cond_a

    const-string p0, "executor not loaded"

    :cond_a
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->importFailed(Ljava/lang/String;)V

    return-void

    .line 687
    :cond_e
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lorg/vekendian/nexus/extensions/NexusHost$7;

    invoke-direct {v1, p0}, Lorg/vekendian/nexus/extensions/NexusHost$7;-><init>(Landroid/net/Uri;)V

    const-string p0, "NexusExtensions:import"

    invoke-direct {v0, v1, p0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 692
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    return-void
.end method

.method private static importUriNow(Landroid/net/Uri;)V
    .registers 3

    .line 696
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->probeReadable(Landroid/net/Uri;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_a

    .line 698
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->importFailed(Ljava/lang/String;)V

    return-void

    .line 702
    :cond_a
    :try_start_a
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    invoke-interface {v0, v1, p0}, Lorg/vekendian/nexus/api/NexusExecutor;->add(Landroid/content/Context;Landroid/net/Uri;)Ljava/lang/String;

    move-result-object p0

    .line 703
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "import -> "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    if-nez p0, :cond_21

    const-string v1, "rejected"

    goto :goto_22

    :cond_21
    move-object v1, p0

    :goto_22
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    if-nez p0, :cond_34

    const-string p0, "the picked file is not a loadable extension (.lua or .jar)"

    .line 705
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->importFailed(Ljava/lang/String;)V

    return-void

    .line 708
    :cond_34
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->rerender()V
    :try_end_37
    .catchall {:try_start_a .. :try_end_37} :catchall_38

    goto :goto_40

    :catchall_38
    move-exception p0

    .line 710
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->importFailed(Ljava/lang/String;)V

    :goto_40
    return-void
.end method

.method static log(Ljava/lang/String;)V
    .registers 2

    const-string v0, "NexusMod"

    .line 677
    invoke-static {v0, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method

.method private static markChosen(Landroid/widget/Button;ZI)V
    .registers 4

    const/4 v0, 0x0

    if-eqz p1, :cond_9

    if-eqz p2, :cond_9

    .line 654
    invoke-virtual {p0, v0, v0, p2, v0}, Landroid/widget/Button;->setCompoundDrawablesRelativeWithIntrinsicBounds(IIII)V

    goto :goto_c

    .line 656
    :cond_9
    invoke-virtual {p0, v0, v0, v0, v0}, Landroid/widget/Button;->setCompoundDrawablesRelativeWithIntrinsicBounds(IIII)V

    :goto_c
    return-void
.end method

.method static onRemoveClicked(Lorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 7

    if-nez p0, :cond_3

    return-void

    .line 949
    :cond_3
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    .line 950
    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->ids:[I

    if-eqz v0, :cond_5f

    if-nez v1, :cond_c

    goto :goto_5f

    .line 955
    :cond_c
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->dialogContext()Landroid/content/Context;

    move-result-object v0

    if-nez v0, :cond_16

    .line 957
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->removeExtension(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    return-void

    .line 960
    :cond_16
    new-instance v2, Landroid/app/AlertDialog$Builder;

    invoke-direct {v2, v0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const/16 v3, 0xe

    aget v3, v1, v3

    .line 961
    invoke-virtual {v2, v3}, Landroid/app/AlertDialog$Builder;->setTitle(I)Landroid/app/AlertDialog$Builder;

    move-result-object v2

    const/16 v3, 0xf

    aget v1, v1, v3

    const/4 v3, 0x1

    new-array v3, v3, [Ljava/lang/Object;

    const/4 v4, 0x0

    .line 963
    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ExtensionInfo;->name()Ljava/lang/String;

    move-result-object v5

    if-nez v5, :cond_36

    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v5

    goto :goto_3a

    :cond_36
    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ExtensionInfo;->name()Ljava/lang/String;

    move-result-object v5

    :goto_3a
    aput-object v5, v3, v4

    .line 962
    invoke-virtual {v0, v1, v3}, Landroid/content/Context;->getString(I[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v2, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    const v2, 0x104000a

    new-instance v3, Lorg/vekendian/nexus/extensions/NexusHost$10;

    invoke-direct {v3, p0}, Lorg/vekendian/nexus/extensions/NexusHost$10;-><init>(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    .line 964
    invoke-virtual {v1, v2, v3}, Landroid/app/AlertDialog$Builder;->setPositiveButton(ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    const/high16 v1, 0x1040000

    const/4 v2, 0x0

    .line 970
    invoke-virtual {p0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    .line 971
    invoke-virtual {p0}, Landroid/app/AlertDialog$Builder;->create()Landroid/app/AlertDialog;

    move-result-object p0

    .line 972
    invoke-static {v0, p0}, Lorg/vekendian/nexus/extensions/NexusHost;->showDialog(Landroid/content/Context;Landroid/app/AlertDialog;)V

    return-void

    .line 952
    :cond_5f
    :goto_5f
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->removeExtension(Lorg/vekendian/nexus/api/ExtensionInfo;)V

    return-void
.end method

.method public static park(Landroid/net/Uri;)V
    .registers 3

    .line 153
    sput-object p0, Lorg/vekendian/nexus/extensions/NexusHost;->pending:Landroid/net/Uri;

    if-eqz p0, :cond_18

    .line 155
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "parked "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :cond_18
    return-void
.end method

.method public static parkFromActivity(Landroid/app/Activity;Landroid/net/Uri;)V
    .registers 4

    if-eqz p1, :cond_26

    if-eqz p0, :cond_26

    .line 142
    :try_start_4
    invoke-virtual {p0}, Landroid/app/Activity;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object p0

    const/4 v0, 0x1

    invoke-virtual {p0, p1, v0}, Landroid/content/ContentResolver;->takePersistableUriPermission(Landroid/net/Uri;I)V
    :try_end_c
    .catchall {:try_start_4 .. :try_end_c} :catchall_d

    goto :goto_26

    :catchall_d
    move-exception p0

    .line 145
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "persistable grant refused at pick: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    .line 148
    :cond_26
    :goto_26
    invoke-static {p1}, Lorg/vekendian/nexus/extensions/NexusHost;->park(Landroid/net/Uri;)V

    return-void
.end method

.method private static permissionButton(Landroid/content/Context;I)Landroid/widget/Button;
    .registers 3

    const/4 v0, 0x1

    .line 589
    invoke-static {p0, p1, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;

    move-result-object p0

    return-object p0
.end method

.method private static permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;
    .registers 6

    .line 593
    new-instance v0, Landroid/widget/Button;

    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 594
    invoke-virtual {v0, p1}, Landroid/widget/Button;->setText(I)V

    const/4 p1, 0x0

    .line 595
    invoke-virtual {v0, p1}, Landroid/widget/Button;->setAllCaps(Z)V

    const/16 v1, 0x11

    .line 596
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setGravity(I)V

    const/16 v1, 0x58

    .line 597
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v2

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setMinWidth(I)V

    .line 598
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v1

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setMinimumWidth(I)V

    const/16 v1, 0xa

    .line 599
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v2

    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v1

    invoke-virtual {v0, v2, p1, v1, p1}, Landroid/widget/Button;->setPadding(IIII)V

    if-eqz p2, :cond_33

    const-string v1, "nexus_bg_choice"

    goto :goto_35

    :cond_33
    const-string v1, "nexus_bg_button"

    :goto_35
    const-string v2, "drawable"

    .line 600
    invoke-static {p0, v1, v2}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v1

    if-eqz v1, :cond_40

    .line 603
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setBackgroundResource(I)V

    :cond_40
    const/4 v1, 0x0

    .line 608
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    if-eqz p2, :cond_5c

    const-string p2, "nexus_choice_text"

    const-string v1, "color"

    .line 610
    invoke-static {p0, p2, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result p2

    if-eqz p2, :cond_66

    .line 612
    invoke-virtual {v0}, Landroid/widget/Button;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    invoke-virtual {v1, p2}, Landroid/content/res/Resources;->getColorStateList(I)Landroid/content/res/ColorStateList;

    move-result-object p2

    invoke-virtual {v0, p2}, Landroid/widget/Button;->setTextColor(Landroid/content/res/ColorStateList;)V

    goto :goto_66

    :cond_5c
    const/4 p2, -0x1

    const-string v1, "nexus_text"

    .line 615
    invoke-static {p0, v1, p2}, Lorg/vekendian/nexus/extensions/NexusHost;->colorValue(Landroid/content/Context;Ljava/lang/String;I)I

    move-result p2

    invoke-virtual {v0, p2}, Landroid/widget/Button;->setTextColor(I)V

    .line 617
    :cond_66
    :goto_66
    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v1, -0x2

    invoke-direct {p2, v1, v1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/4 v1, 0x6

    .line 620
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result p0

    invoke-virtual {p2, p0, p1, p1, p1}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    .line 621
    invoke-virtual {v0, p2}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method public static permissions(Landroid/content/Context;[I)V
    .registers 23

    move-object/from16 v0, p1

    const-string v1, ""

    if-eqz p0, :cond_20e

    if-eqz v0, :cond_20e

    .line 279
    array-length v2, v0

    const/16 v3, 0xb

    if-ge v2, v3, :cond_f

    goto/16 :goto_20e

    .line 282
    :cond_f
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->dialogContext()Landroid/content/Context;

    move-result-object v2

    if-nez v2, :cond_1b

    const-string v0, "permissions dialog needs a running Nexus host"

    .line 284
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    return-void

    .line 288
    :cond_1b
    :try_start_1b
    invoke-static {}, Lorg/vekendian/nexus/extensions/LuaBridge;->migrateBroadGrants()V

    .line 289
    invoke-static {}, Lorg/vekendian/nexus/extensions/LuaBridge;->capabilities()[Ljava/lang/String;

    move-result-object v3

    .line 290
    array-length v4, v3

    new-array v10, v4, [Landroid/widget/Button;

    .line 291
    array-length v4, v3

    new-array v11, v4, [Landroid/widget/Button;

    const/4 v12, 0x1

    new-array v13, v12, [Landroid/app/AlertDialog;

    .line 294
    new-instance v14, Landroid/widget/LinearLayout;

    invoke-direct {v14, v2}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 295
    invoke-virtual {v14, v12}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v4, 0x14

    .line 296
    invoke-static {v2, v4}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v5

    const/16 v6, 0x8

    invoke-static {v2, v6}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v6

    invoke-static {v2, v4}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v4

    const/4 v15, 0x4

    invoke-static {v2, v15}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v7

    invoke-virtual {v14, v5, v6, v4, v7}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 300
    new-instance v4, Landroid/widget/TextView;

    invoke-direct {v4, v2}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v5, "nexus_str_perm_default_note"

    .line 301
    invoke-static {v2, v5, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->text(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/high16 v9, 0x41400000    # 12.0f

    .line 302
    invoke-virtual {v4, v9}, Landroid/widget/TextView;->setTextSize(F)V

    const-string v5, "nexus_orange_dim"

    const/16 v6, -0x4c9a

    .line 303
    invoke-static {v2, v5, v6}, Lorg/vekendian/nexus/extensions/NexusHost;->colorValue(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v5

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setTextColor(I)V

    .line 304
    invoke-static {v2, v15}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v5

    const/4 v8, 0x0

    invoke-virtual {v4, v8, v8, v8, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 305
    invoke-virtual {v14, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    const/4 v7, 0x0

    .line 307
    :goto_75
    array-length v4, v3

    const/4 v5, 0x6

    if-ge v7, v4, :cond_13f

    .line 308
    aget-object v6, v3, v7

    .line 309
    new-instance v4, Landroid/widget/LinearLayout;

    invoke-direct {v4, v2}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 310
    invoke-virtual {v4, v8}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v15, 0x10

    .line 311
    invoke-virtual {v4, v15}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 312
    invoke-static {v2, v5}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v15

    invoke-static {v2, v5}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v5

    invoke-virtual {v4, v8, v15, v8, v5}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 316
    new-instance v5, Landroid/widget/LinearLayout;

    invoke-direct {v5, v2}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 317
    invoke-virtual {v5, v12}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 319
    new-instance v15, Landroid/widget/TextView;

    invoke-direct {v15, v2}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    add-int/lit8 v12, v7, 0x8

    .line 320
    array-length v8, v0

    if-ge v12, v8, :cond_ab

    .line 321
    aget v8, v0, v12

    invoke-virtual {v15, v8}, Landroid/widget/TextView;->setText(I)V

    goto :goto_ae

    .line 323
    :cond_ab
    invoke-virtual {v15, v6}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :goto_ae
    const/high16 v8, 0x41700000    # 15.0f

    .line 325
    invoke-virtual {v15, v8}, Landroid/widget/TextView;->setTextSize(F)V

    .line 326
    invoke-virtual {v5, v15}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 328
    invoke-static {v6}, Lorg/vekendian/nexus/extensions/LuaBridge;->scriptOverride(Ljava/lang/String;)Z

    move-result v8

    if-eqz v8, :cond_dc

    .line 329
    new-instance v8, Landroid/widget/TextView;

    invoke-direct {v8, v2}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v12, "nexus_str_perm_script_override"

    .line 330
    invoke-static {v2, v12, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->text(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v12

    invoke-virtual {v8, v12}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 331
    invoke-virtual {v8, v9}, Landroid/widget/TextView;->setTextSize(F)V

    const-string v12, "nexus_text2"

    const v15, -0x575750

    .line 332
    invoke-static {v2, v12, v15}, Lorg/vekendian/nexus/extensions/NexusHost;->colorValue(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v12

    invoke-virtual {v8, v12}, Landroid/widget/TextView;->setTextColor(I)V

    .line 333
    invoke-virtual {v5, v8}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 335
    :cond_dc
    new-instance v8, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v12, -0x2

    const/high16 v15, 0x3f800000    # 1.0f

    const/4 v9, 0x0

    invoke-direct {v8, v9, v12, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v5, v8}, Landroid/widget/LinearLayout;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 337
    invoke-virtual {v4, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    const/4 v5, 0x1

    .line 339
    aget v8, v0, v5

    invoke-static {v2, v8}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;I)Landroid/widget/Button;

    move-result-object v12

    const/4 v5, 0x2

    .line 340
    aget v5, v0, v5

    invoke-static {v2, v5}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;I)Landroid/widget/Button;

    move-result-object v15

    .line 341
    aput-object v12, v10, v7

    .line 342
    aput-object v15, v11, v7

    .line 343
    new-instance v8, Lorg/vekendian/nexus/extensions/NexusHost$1;

    move-object v5, v4

    move-object v4, v8

    move-object/from16 v16, v1

    move-object v1, v5

    move-object v5, v6

    move-object/from16 v18, v6

    move-object v6, v2

    move/from16 v19, v7

    move-object v7, v3

    move-object v9, v8

    move-object/from16 v20, v13

    const/4 v13, 0x0

    move-object v8, v10

    move-object v13, v9

    const/high16 v17, 0x41400000    # 12.0f

    move-object v9, v11

    invoke-direct/range {v4 .. v9}, Lorg/vekendian/nexus/extensions/NexusHost$1;-><init>(Ljava/lang/String;Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    invoke-virtual {v12, v13}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 349
    new-instance v13, Lorg/vekendian/nexus/extensions/NexusHost$2;

    move-object v4, v13

    move-object/from16 v5, v18

    move-object v6, v2

    move-object v7, v3

    move-object v8, v10

    move-object v9, v11

    invoke-direct/range {v4 .. v9}, Lorg/vekendian/nexus/extensions/NexusHost$2;-><init>(Ljava/lang/String;Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    invoke-virtual {v15, v13}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 355
    invoke-virtual {v1, v12}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 356
    invoke-virtual {v1, v15}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 357
    invoke-virtual {v14, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    add-int/lit8 v7, v19, 0x1

    move-object/from16 v1, v16

    move-object/from16 v13, v20

    const/4 v8, 0x0

    const/high16 v9, 0x41400000    # 12.0f

    const/4 v12, 0x1

    const/4 v15, 0x4

    goto/16 :goto_75

    :cond_13f
    move-object/from16 v20, v13

    .line 360
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, v2}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v4, 0x0

    .line 361
    invoke-virtual {v1, v4}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v6, 0xa

    .line 362
    invoke-static {v2, v6}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v6

    invoke-virtual {v1, v4, v6, v4, v4}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const/4 v6, 0x3

    .line 363
    aget v6, v0, v6

    invoke-static {v2, v6, v4}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;

    move-result-object v6

    .line 364
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/NexusHost;->footerParams(Landroid/content/Context;)Landroid/widget/LinearLayout$LayoutParams;

    move-result-object v4

    invoke-virtual {v6, v4}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 365
    new-instance v4, Lorg/vekendian/nexus/extensions/NexusHost$3;

    invoke-direct {v4, v3, v2, v10, v11}, Lorg/vekendian/nexus/extensions/NexusHost$3;-><init>([Ljava/lang/String;Landroid/content/Context;[Landroid/widget/Button;[Landroid/widget/Button;)V

    invoke-virtual {v6, v4}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    const/4 v4, 0x4

    .line 373
    aget v4, v0, v4

    const/4 v7, 0x0

    invoke-static {v2, v4, v7}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;

    move-result-object v4

    .line 374
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/NexusHost;->footerParams(Landroid/content/Context;)Landroid/widget/LinearLayout$LayoutParams;

    move-result-object v7

    invoke-virtual {v4, v7}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 375
    new-instance v7, Lorg/vekendian/nexus/extensions/NexusHost$4;

    invoke-direct {v7, v3, v2, v10, v11}, Lorg/vekendian/nexus/extensions/NexusHost$4;-><init>([Ljava/lang/String;Landroid/content/Context;[Landroid/widget/Button;[Landroid/widget/Button;)V

    invoke-virtual {v4, v7}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 383
    invoke-virtual {v1, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 384
    invoke-virtual {v1, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 385
    invoke-virtual {v14, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 387
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, v2}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v4, 0x0

    .line 388
    invoke-virtual {v1, v4}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 389
    invoke-static {v2, v5}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v5

    invoke-virtual {v1, v4, v5, v4, v4}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const/4 v5, 0x5

    .line 390
    aget v5, v0, v5

    invoke-static {v2, v5, v4}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;

    move-result-object v5

    .line 391
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/NexusHost;->footerParams(Landroid/content/Context;)Landroid/widget/LinearLayout$LayoutParams;

    move-result-object v4

    invoke-virtual {v5, v4}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 392
    new-instance v4, Lorg/vekendian/nexus/extensions/NexusHost$5;

    invoke-direct {v4, v2, v0}, Lorg/vekendian/nexus/extensions/NexusHost$5;-><init>(Landroid/content/Context;[I)V

    invoke-virtual {v5, v4}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    const/4 v4, 0x7

    .line 398
    aget v4, v0, v4

    const/4 v6, 0x0

    invoke-static {v2, v4, v6}, Lorg/vekendian/nexus/extensions/NexusHost;->permissionButton(Landroid/content/Context;IZ)Landroid/widget/Button;

    move-result-object v4

    .line 399
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/NexusHost;->footerParams(Landroid/content/Context;)Landroid/widget/LinearLayout$LayoutParams;

    move-result-object v6

    invoke-virtual {v4, v6}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 400
    new-instance v6, Lorg/vekendian/nexus/extensions/NexusHost$6;

    move-object/from16 v7, v20

    invoke-direct {v6, v7}, Lorg/vekendian/nexus/extensions/NexusHost$6;-><init>([Landroid/app/AlertDialog;)V

    invoke-virtual {v4, v6}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 407
    invoke-virtual {v1, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 408
    invoke-virtual {v1, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 409
    invoke-virtual {v14, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 411
    new-instance v1, Landroid/app/AlertDialog$Builder;

    invoke-direct {v1, v2}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const/4 v4, 0x0

    aget v0, v0, v4

    .line 412
    invoke-virtual {v1, v0}, Landroid/app/AlertDialog$Builder;->setTitle(I)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 413
    invoke-virtual {v0, v14}, Landroid/app/AlertDialog$Builder;->setView(Landroid/view/View;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const/4 v1, 0x1

    .line 414
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setCancelable(Z)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 415
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->create()Landroid/app/AlertDialog;

    move-result-object v0

    aput-object v0, v7, v4

    .line 416
    invoke-static {v2, v3, v10, v11}, Lorg/vekendian/nexus/extensions/NexusHost;->syncPermissionButtons(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V

    aget-object v0, v7, v4

    .line 417
    invoke-static {v2, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->showDialog(Landroid/content/Context;Landroid/app/AlertDialog;)V
    :try_end_1f4
    .catchall {:try_start_1b .. :try_end_1f4} :catchall_1f5

    goto :goto_20e

    :catchall_1f5
    move-exception v0

    .line 419
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "permissions dialog failed: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :cond_20e
    :goto_20e
    return-void
.end method

.method public static pick(Landroid/app/Activity;)V
    .registers 4

    if-nez p0, :cond_3

    return-void

    .line 117
    :cond_3
    :try_start_3
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.OPEN_DOCUMENT"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v1, "android.intent.category.OPENABLE"

    .line 118
    invoke-virtual {v0, v1}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;

    const-string v1, "*/*"

    .line 119
    invoke-virtual {v0, v1}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    const-string v1, "android.intent.extra.MIME_TYPES"

    .line 120
    sget-object v2, Lorg/vekendian/nexus/extensions/NexusHost;->PICK_MIME:[Ljava/lang/String;

    invoke-virtual {v0, v1, v2}, Landroid/content/Intent;->putExtra(Ljava/lang/String;[Ljava/lang/String;)Landroid/content/Intent;

    const-string v1, "org.vekendian.nexus.ModulePicker"

    .line 121
    invoke-virtual {v0, p0, v1}, Landroid/content/Intent;->setClassName(Landroid/content/Context;Ljava/lang/String;)Landroid/content/Intent;

    .line 122
    invoke-virtual {p0, v0}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V
    :try_end_23
    .catchall {:try_start_3 .. :try_end_23} :catchall_24

    goto :goto_3d

    :catchall_24
    move-exception p0

    .line 124
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "picker failed: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :goto_3d
    return-void
.end method

.method public static powerOff()V
    .registers 3

    .line 238
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-nez v0, :cond_5

    return-void

    .line 242
    :cond_5
    :try_start_5
    invoke-interface {v0}, Lorg/vekendian/nexus/api/NexusExecutor;->stopAll()V
    :try_end_8
    .catchall {:try_start_5 .. :try_end_8} :catchall_9

    goto :goto_22

    :catchall_9
    move-exception v0

    .line 244
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "stopAll failed: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :goto_22
    return-void
.end method

.method public static powerOn()V
    .registers 3

    .line 214
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-nez v0, :cond_5

    return-void

    .line 218
    :cond_5
    :try_start_5
    invoke-interface {v0}, Lorg/vekendian/nexus/api/NexusExecutor;->runAll()V
    :try_end_8
    .catchall {:try_start_5 .. :try_end_8} :catchall_9

    goto :goto_22

    :catchall_9
    move-exception v0

    .line 220
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "runAll failed: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :goto_22
    return-void
.end method

.method private static probeReadable(Landroid/net/Uri;)Ljava/lang/String;
    .registers 4

    const/4 v0, 0x0

    .line 718
    :try_start_1
    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->app:Landroid/content/Context;

    invoke-virtual {v1}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v1

    invoke-virtual {v1, p0}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object p0
    :try_end_b
    .catchall {:try_start_1 .. :try_end_b} :catchall_2b

    if-nez p0, :cond_15

    :try_start_d
    const-string v0, "the picked file cannot be opened"
    :try_end_f
    .catchall {:try_start_d .. :try_end_f} :catchall_29

    if-eqz p0, :cond_14

    .line 731
    :try_start_11
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_14
    .catchall {:try_start_11 .. :try_end_14} :catchall_14

    :catchall_14
    :cond_14
    return-object v0

    .line 722
    :cond_15
    :try_start_15
    invoke-virtual {p0}, Ljava/io/InputStream;->read()I

    move-result v1

    if-gez v1, :cond_23

    const-string v0, "the picked file is empty"
    :try_end_1d
    .catchall {:try_start_15 .. :try_end_1d} :catchall_29

    if-eqz p0, :cond_22

    .line 731
    :try_start_1f
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_22
    .catchall {:try_start_1f .. :try_end_22} :catchall_22

    :catchall_22
    :cond_22
    return-object v0

    :cond_23
    if-eqz p0, :cond_28

    :try_start_25
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_28
    .catchall {:try_start_25 .. :try_end_28} :catchall_28

    :catchall_28
    :cond_28
    return-object v0

    :catchall_29
    move-exception v0

    goto :goto_2f

    :catchall_2b
    move-exception p0

    move-object v2, v0

    move-object v0, p0

    move-object p0, v2

    .line 727
    :goto_2f
    :try_start_2f
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v0
    :try_end_33
    .catchall {:try_start_2f .. :try_end_33} :catchall_39

    if-eqz p0, :cond_38

    .line 731
    :try_start_35
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_38
    .catchall {:try_start_35 .. :try_end_38} :catchall_38

    :catchall_38
    :cond_38
    return-object v0

    :catchall_39
    move-exception v0

    if-eqz p0, :cond_3f

    :try_start_3c
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_3f
    .catchall {:try_start_3c .. :try_end_3f} :catchall_3f

    .line 736
    :catchall_3f
    :cond_3f
    throw v0
.end method

.method private static removeExtension(Lorg/vekendian/nexus/api/ExtensionInfo;)V
    .registers 3

    .line 913
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    if-eqz v0, :cond_4e

    if-nez p0, :cond_7

    goto :goto_4e

    .line 917
    :cond_7
    :try_start_7
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "remove "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, " -> "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->executor:Lorg/vekendian/nexus/api/NexusExecutor;

    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object p0

    invoke-interface {v1, p0}, Lorg/vekendian/nexus/api/NexusExecutor;->remove(Ljava/lang/String;)Z

    move-result p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V
    :try_end_31
    .catchall {:try_start_7 .. :try_end_31} :catchall_32

    goto :goto_4b

    :catchall_32
    move-exception p0

    .line 919
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "remove failed: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    .line 921
    :goto_4b
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->rerender()V

    :cond_4e
    :goto_4e
    return-void
.end method

.method public static render(Landroid/app/Activity;IIIIIIIIIIIIIIII)V
    .registers 20

    move-object v0, p0

    if-nez v0, :cond_4

    return-void

    .line 204
    :cond_4
    sput-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    const/16 v1, 0x10

    new-array v1, v1, [I

    const/4 v2, 0x0

    aput p1, v1, v2

    const/4 v2, 0x1

    aput p2, v1, v2

    const/4 v2, 0x2

    aput p3, v1, v2

    const/4 v2, 0x3

    aput p4, v1, v2

    const/4 v2, 0x4

    aput p5, v1, v2

    const/4 v2, 0x5

    aput p6, v1, v2

    const/4 v2, 0x6

    aput p7, v1, v2

    const/4 v2, 0x7

    aput p8, v1, v2

    const/16 v2, 0x8

    aput p9, v1, v2

    const/16 v2, 0x9

    aput p10, v1, v2

    const/16 v2, 0xa

    aput p11, v1, v2

    const/16 v2, 0xb

    aput p12, v1, v2

    const/16 v2, 0xc

    aput p13, v1, v2

    const/16 v2, 0xd

    aput p14, v1, v2

    const/16 v2, 0xe

    aput p15, v1, v2

    const/16 v2, 0xf

    aput p16, v1, v2

    .line 205
    sput-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->ids:[I

    .line 209
    invoke-static {p0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->draw(Landroid/app/Activity;[I)V

    return-void
.end method

.method static rerender()V
    .registers 3

    .line 931
    sget-object v0, Lorg/vekendian/nexus/extensions/NexusHost;->activity:Landroid/app/Activity;

    .line 932
    sget-object v1, Lorg/vekendian/nexus/extensions/NexusHost;->ids:[I

    if-eqz v0, :cond_11

    if-nez v1, :cond_9

    goto :goto_11

    .line 936
    :cond_9
    new-instance v2, Lorg/vekendian/nexus/extensions/NexusHost$9;

    invoke-direct {v2, v0, v1}, Lorg/vekendian/nexus/extensions/NexusHost$9;-><init>(Landroid/app/Activity;[I)V

    invoke-virtual {v0, v2}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    :cond_11
    :goto_11
    return-void
.end method

.method static resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I
    .registers 4

    .line 525
    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    .line 526
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object p0

    .line 525
    invoke-virtual {v0, p1, p2, p0}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I

    move-result p0
    :try_end_c
    .catchall {:try_start_0 .. :try_end_c} :catchall_d

    return p0

    :catchall_d
    const/4 p0, 0x0

    return p0
.end method

.method private static showDialog(Landroid/content/Context;Landroid/app/AlertDialog;)V
    .registers 8

    if-eqz p0, :cond_aa

    if-nez p1, :cond_6

    goto/16 :goto_aa

    .line 479
    :cond_6
    invoke-virtual {p1}, Landroid/app/AlertDialog;->getWindow()Landroid/view/Window;

    move-result-object v0

    const-string v1, "drawable"

    if-eqz v0, :cond_44

    const-string v2, "nexus_bg_dialog"

    .line 481
    invoke-static {p0, v2, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v2

    if-eqz v2, :cond_19

    .line 483
    invoke-virtual {v0, v2}, Landroid/view/Window;->setBackgroundDrawableResource(I)V

    .line 486
    :cond_19
    :try_start_19
    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v3, 0x1a

    if-lt v2, v3, :cond_25

    const/16 v2, 0x7f6

    .line 487
    invoke-virtual {v0, v2}, Landroid/view/Window;->setType(I)V

    goto :goto_44

    :cond_25
    const/16 v2, 0x7d2

    .line 489
    invoke-virtual {v0, v2}, Landroid/view/Window;->setType(I)V
    :try_end_2a
    .catchall {:try_start_19 .. :try_end_2a} :catchall_2b

    goto :goto_44

    :catchall_2b
    move-exception v0

    .line 492
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "dialog overlay type failed: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    .line 496
    :cond_44
    :goto_44
    :try_start_44
    invoke-virtual {p1}, Landroid/app/AlertDialog;->show()V
    :try_end_47
    .catchall {:try_start_44 .. :try_end_47} :catchall_91

    const/4 v0, -0x1

    .line 501
    invoke-virtual {p1, v0}, Landroid/app/AlertDialog;->getButton(I)Landroid/widget/Button;

    move-result-object v0

    const/4 v2, -0x2

    .line 502
    invoke-virtual {p1, v2}, Landroid/app/AlertDialog;->getButton(I)Landroid/widget/Button;

    move-result-object v2

    const/4 v3, -0x3

    .line 503
    invoke-virtual {p1, v3}, Landroid/app/AlertDialog;->getButton(I)Landroid/widget/Button;

    move-result-object p1

    const/16 v3, 0xc

    .line 504
    invoke-static {p0, v3}, Lorg/vekendian/nexus/extensions/NexusHost;->dp(Landroid/content/Context;I)I

    move-result v3

    const/4 v4, 0x0

    if-eqz v0, :cond_73

    const-string v5, "nexus_bg_primary"

    .line 506
    invoke-static {p0, v5, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v1

    if-eqz v1, :cond_6a

    .line 508
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setBackgroundResource(I)V

    :cond_6a
    const v1, -0xe5e5e4

    .line 510
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextColor(I)V

    .line 511
    invoke-virtual {v0, v3, v4, v3, v4}, Landroid/widget/Button;->setPadding(IIII)V

    :cond_73
    const v0, -0x575750

    const-string v1, "nexus_text2"

    if-eqz v2, :cond_84

    .line 514
    invoke-static {p0, v1, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->colorValue(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v5

    invoke-virtual {v2, v5}, Landroid/widget/Button;->setTextColor(I)V

    .line 515
    invoke-virtual {v2, v3, v4, v3, v4}, Landroid/widget/Button;->setPadding(IIII)V

    :cond_84
    if-eqz p1, :cond_90

    .line 518
    invoke-static {p0, v1, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->colorValue(Landroid/content/Context;Ljava/lang/String;I)I

    move-result p0

    invoke-virtual {p1, p0}, Landroid/widget/Button;->setTextColor(I)V

    .line 519
    invoke-virtual {p1, v3, v4, v3, v4}, Landroid/widget/Button;->setPadding(IIII)V

    :cond_90
    return-void

    :catchall_91
    move-exception p0

    .line 498
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "dialog show failed: "

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/NexusHost;->log(Ljava/lang/String;)V

    :cond_aa
    :goto_aa
    return-void
.end method

.method static statusColor(Landroid/content/Context;Lorg/vekendian/nexus/api/ExtensionInfo;)I
    .registers 5

    .line 874
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v0

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->JAR:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    const-string v2, "nexus_ok"

    if-eq v0, v1, :cond_3a

    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->type()Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    move-result-object v0

    sget-object v1, Lorg/vekendian/nexus/api/ExtensionInfo$Type;->DEX:Lorg/vekendian/nexus/api/ExtensionInfo$Type;

    if-ne v0, v1, :cond_13

    goto :goto_3a

    .line 877
    :cond_13
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->state()I

    move-result p1

    const/4 v0, 0x1

    if-eq p1, v0, :cond_35

    const/4 v0, 0x2

    if-eq p1, v0, :cond_2e

    const/4 v0, 0x4

    if-eq p1, v0, :cond_27

    const-string p1, "nexus_text2"

    .line 885
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p0

    return p0

    :cond_27
    const-string p1, "nexus_bad"

    .line 881
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p0

    return p0

    :cond_2e
    const-string p1, "nexus_text"

    .line 883
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p0

    return p0

    .line 879
    :cond_35
    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p0

    return p0

    .line 875
    :cond_3a
    :goto_3a
    invoke-static {p0, v2}, Lorg/vekendian/nexus/extensions/NexusHost;->color(Landroid/content/Context;Ljava/lang/String;)I

    move-result p0

    return p0
.end method

.method private static syncPermissionButtons(Landroid/content/Context;[Ljava/lang/String;[Landroid/widget/Button;[Landroid/widget/Button;)V
    .registers 9

    const-string v0, "nexus_ic_check"

    const-string v1, "drawable"

    .line 636
    invoke-static {p0, v0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result p0

    const/4 v0, 0x0

    .line 637
    :goto_9
    array-length v1, p1

    if-ge v0, v1, :cond_3c

    .line 638
    aget-object v1, p1, v0

    invoke-static {v1}, Lorg/vekendian/nexus/extensions/LuaBridge;->global(Ljava/lang/String;)Z

    move-result v1

    .line 639
    aget-object v2, p2, v0

    const/4 v3, 0x1

    if-eqz v2, :cond_24

    .line 640
    invoke-virtual {v2, v1}, Landroid/widget/Button;->setSelected(Z)V

    .line 641
    aget-object v2, p2, v0

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setEnabled(Z)V

    .line 642
    aget-object v2, p2, v0

    invoke-static {v2, v1, p0}, Lorg/vekendian/nexus/extensions/NexusHost;->markChosen(Landroid/widget/Button;ZI)V

    .line 644
    :cond_24
    aget-object v2, p3, v0

    if-eqz v2, :cond_39

    xor-int/lit8 v4, v1, 0x1

    .line 645
    invoke-virtual {v2, v4}, Landroid/widget/Button;->setSelected(Z)V

    .line 646
    aget-object v2, p3, v0

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setEnabled(Z)V

    .line 647
    aget-object v2, p3, v0

    xor-int/lit8 v1, v1, 0x1

    invoke-static {v2, v1, p0}, Lorg/vekendian/nexus/extensions/NexusHost;->markChosen(Landroid/widget/Button;ZI)V

    :cond_39
    add-int/lit8 v0, v0, 0x1

    goto :goto_9

    :cond_3c
    return-void
.end method

.method private static text(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .registers 4

    const-string v0, "string"

    .line 540
    invoke-static {p0, p1, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result p1

    if-nez p1, :cond_9

    return-object p2

    .line 545
    :cond_9
    :try_start_9
    invoke-virtual {p0, p1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object p0
    :try_end_d
    .catchall {:try_start_9 .. :try_end_d} :catchall_e

    return-object p0

    :catchall_e
    return-object p2
.end method

.method private static themedContext(Landroid/content/Context;)Landroid/content/Context;
    .registers 3

    const-string v0, "NexusDialog"

    const-string v1, "style"

    .line 436
    invoke-static {p0, v0, v1}, Lorg/vekendian/nexus/extensions/NexusHost;->resourceId(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_d

    const v0, 0x1030226

    .line 440
    :cond_d
    new-instance v1, Landroid/view/ContextThemeWrapper;

    invoke-direct {v1, p0, v0}, Landroid/view/ContextThemeWrapper;-><init>(Landroid/content/Context;I)V

    return-object v1
.end method

.method private static toast(Landroid/content/Context;Ljava/lang/String;)V
    .registers 3

    const/4 v0, 0x0

    .line 233
    invoke-static {p0, p1, v0}, Lorg/vekendian/nexus/extensions/NexusToast;->show(Landroid/content/Context;Ljava/lang/String;I)V

    return-void
.end method
