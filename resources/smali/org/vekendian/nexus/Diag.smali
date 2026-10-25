.class public final Lorg/vekendian/nexus/Diag;
.super Ljava/lang/Object;
.source "Diag.java"


# static fields
.field private static final ID_ADDR_ITEM_TYPE:I = 0x7f050008

.field private static final ID_ADDR_LIST:I = 0x7f05000a

.field private static final L_SERVICE_DIALOG:I = 0x7f06001d

.field private static final TAG:Ljava/lang/String; = "NexusDiag"


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 57
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static describe(Ljava/lang/Object;)Ljava/lang/String;
    .registers 1

    if-nez p0, :cond_5

    const-string p0, "null"

    return-object p0

    .line 183
    :cond_5
    :try_start_5
    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object p0
    :try_end_d
    .catchall {:try_start_5 .. :try_end_d} :catchall_e

    return-object p0

    :catchall_e
    const-string p0, "<describe failed>"

    return-object p0
.end method

.method private static inflate(Landroid/content/Context;)Landroid/view/View;
    .registers 10

    const v0, 0x7f06001d

    const/4 v1, 0x0

    :try_start_4
    const-string v2, "android.ext.a$d"

    .line 134
    invoke-static {v2}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    const-string v3, "f"

    const/4 v4, 0x2

    new-array v5, v4, [Ljava/lang/Class;

    sget-object v6, Ljava/lang/Integer;->TYPE:Ljava/lang/Class;

    const/4 v7, 0x0

    aput-object v6, v5, v7

    const-class v6, Landroid/view/ViewGroup;

    const/4 v8, 0x1

    aput-object v6, v5, v8

    .line 135
    invoke-virtual {v2, v3, v5}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v2

    new-array v3, v4, [Ljava/lang/Object;

    .line 136
    invoke-static {v0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v4

    aput-object v4, v3, v7

    aput-object v1, v3, v8

    invoke-virtual {v2, v1, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/view/View;
    :try_end_2d
    .catchall {:try_start_4 .. :try_end_2d} :catchall_2e

    return-object v2

    :catchall_2e
    move-exception v2

    .line 138
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "  La/d.f unavailable ("

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v2}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "); using LayoutInflater.inflate"

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 139
    invoke-static {p0}, Landroid/view/LayoutInflater;->from(Landroid/content/Context;)Landroid/view/LayoutInflater;

    move-result-object p0

    invoke-virtual {p0, v0, v1}, Landroid/view/LayoutInflater;->inflate(ILandroid/view/ViewGroup;)Landroid/view/View;

    move-result-object p0

    return-object p0
.end method

.method private static log(Ljava/lang/String;)V
    .registers 2

    const-string v0, "NexusDiag"

    .line 190
    invoke-static {v0, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method

.method private static mainServiceContext()Landroid/content/Context;
    .registers 4

    const/4 v0, 0x0

    :try_start_1
    const-string v1, "android.ext.MainService"

    .line 119
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    const-string v2, "context"

    .line 120
    invoke-virtual {v1, v2}, Ljava/lang/Class;->getField(Ljava/lang/String;)Ljava/lang/reflect/Field;

    move-result-object v1

    invoke-virtual {v1, v0}, Ljava/lang/reflect/Field;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/content/Context;
    :try_end_13
    .catchall {:try_start_1 .. :try_end_13} :catchall_14

    return-object v1

    :catchall_14
    move-exception v1

    .line 122
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "  could not read MainService.context: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, ": "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 123
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 122
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    return-object v0
.end method

.method public static probe()V
    .registers 4

    :try_start_0
    const-string v0, "===== MainService init probe ====="

    .line 62
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 63
    invoke-static {}, Lorg/vekendian/nexus/Diag;->mainServiceContext()Landroid/content/Context;

    move-result-object v0

    .line 64
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  MainService.context = "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    if-nez v0, :cond_29

    const-string v0, "  (null -- Z() could not even inflate; this is not the crash we know)"

    .line 67
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    return-void

    .line 71
    :cond_29
    invoke-static {v0}, Landroid/view/LayoutInflater;->from(Landroid/content/Context;)Landroid/view/LayoutInflater;

    move-result-object v1

    .line 72
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "  LayoutInflater.from(ctx) = "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 73
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "  is GG\'s android.ext.a$d = "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    if-eqz v1, :cond_63

    .line 74
    invoke-virtual {v1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v1

    const-string v3, "android.ext.a$d"

    invoke-virtual {v1, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_63

    const/4 v1, 0x1

    goto :goto_64

    :cond_63
    const/4 v1, 0x0

    :goto_64
    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 73
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    const-string v1, "window"

    .line 76
    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v1

    .line 77
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "  getSystemService(\"window\") = "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, "   <- Z():4343 check-casts this to WindowManager; a CCE or NPE here is swallowed by :catchall_1"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    if-eqz v1, :cond_9c

    .line 80
    instance-of v1, v1, Landroid/view/WindowManager;

    if-nez v1, :cond_9c

    const-string v1, "  !!! not a WindowManager -- this IS the ClassCastException"

    .line 81
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 84
    :cond_9c
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  getPackageResourcePath() = "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->safePackagePath(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 85
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  ZipFile entries = "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->safeZipEntries(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 87
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->inflate(Landroid/content/Context;)Landroid/view/View;

    move-result-object v0

    .line 88
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  inflate(0x7f06001d service_dialog) = "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    if-nez v0, :cond_f0

    const-string v0, "  !!! inflate returned null"

    .line 90
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    return-void

    :cond_f0
    const v1, 0x7f05000a

    .line 94
    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v1

    .line 95
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "  >>> findViewById(0x7f05000a addr_list) = "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    if-nez v1, :cond_117

    const-string v1, "  !!! THE ANSWER: the inflated layout does NOT contain addr_list. G will be null and Z0 will NPE."

    .line 97
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    goto :goto_126

    .line 99
    :cond_117
    instance-of v1, v1, Landroid/widget/ListView;

    if-nez v1, :cond_121

    const-string v1, "  !!! addr_list is not a ListView: Z()\'s check-cast throws"

    .line 100
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    goto :goto_126

    :cond_121
    const-string v1, "  addr_list is a live ListView -- inflate is fine, so Z() lost G AFTER this point; look at the paths between 4430 and 5160"

    .line 102
    invoke-static {v1}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    .line 106
    :goto_126
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  (for contrast) findViewById(0x7f050008 addr_item_type) on the same tree = "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const v2, 0x7f050008

    .line 107
    invoke-virtual {v0, v2}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, "   <- this is what :catchall_1 binds, and it must be null"

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 106
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    const-string v0, "===== end probe ====="

    .line 109
    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V
    :try_end_14f
    .catchall {:try_start_0 .. :try_end_14f} :catchall_150

    goto :goto_175

    :catchall_150
    move-exception v0

    .line 111
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "  probe itself threw: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, ": "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/vekendian/nexus/Diag;->log(Ljava/lang/String;)V

    :goto_175
    return-void
.end method

.method private static safePackagePath(Landroid/content/Context;)Ljava/lang/String;
    .registers 3

    .line 145
    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getPackageResourcePath()Ljava/lang/String;

    move-result-object p0
    :try_end_4
    .catchall {:try_start_0 .. :try_end_4} :catchall_5

    return-object p0

    :catchall_5
    move-exception p0

    .line 147
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "THREW "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, ": "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method private static safeZipEntries(Landroid/content/Context;)Ljava/lang/String;
    .registers 4

    const/4 v0, 0x0

    .line 157
    :try_start_1
    new-instance v1, Ljava/util/zip/ZipFile;

    invoke-virtual {p0}, Landroid/content/Context;->getPackageResourcePath()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v1, p0}, Ljava/util/zip/ZipFile;-><init>(Ljava/lang/String;)V
    :try_end_a
    .catchall {:try_start_1 .. :try_end_a} :catchall_26

    const/4 p0, 0x0

    .line 159
    :try_start_b
    invoke-virtual {v1}, Ljava/util/zip/ZipFile;->entries()Ljava/util/Enumeration;

    move-result-object v0

    .line 160
    :goto_f
    invoke-interface {v0}, Ljava/util/Enumeration;->hasMoreElements()Z

    move-result v2

    if-eqz v2, :cond_1b

    .line 161
    invoke-interface {v0}, Ljava/util/Enumeration;->nextElement()Ljava/lang/Object;

    add-int/lit8 p0, p0, 0x1

    goto :goto_f

    .line 164
    :cond_1b
    invoke-static {p0}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;

    move-result-object p0
    :try_end_1f
    .catchall {:try_start_b .. :try_end_1f} :catchall_23

    .line 170
    :try_start_1f
    invoke-virtual {v1}, Ljava/util/zip/ZipFile;->close()V
    :try_end_22
    .catchall {:try_start_1f .. :try_end_22} :catchall_22

    :catchall_22
    return-object p0

    :catchall_23
    move-exception p0

    move-object v0, v1

    goto :goto_27

    :catchall_26
    move-exception p0

    .line 166
    :goto_27
    :try_start_27
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "THREW "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/Diag;->describe(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, ": "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0
    :try_end_48
    .catchall {:try_start_27 .. :try_end_48} :catchall_4e

    if-eqz v0, :cond_4d

    .line 170
    :try_start_4a
    invoke-virtual {v0}, Ljava/util/zip/ZipFile;->close()V
    :try_end_4d
    .catchall {:try_start_4a .. :try_end_4d} :catchall_4d

    :catchall_4d
    :cond_4d
    return-object p0

    :catchall_4e
    move-exception p0

    if-eqz v0, :cond_54

    :try_start_51
    invoke-virtual {v0}, Ljava/util/zip/ZipFile;->close()V
    :try_end_54
    .catchall {:try_start_51 .. :try_end_54} :catchall_54

    .line 175
    :catchall_54
    :cond_54
    throw p0
.end method
