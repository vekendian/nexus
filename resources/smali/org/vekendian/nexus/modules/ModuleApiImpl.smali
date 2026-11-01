.class final Lorg/vekendian/nexus/modules/ModuleApiImpl;
.super Ljava/lang/Object;
.source "ModuleApiImpl.java"

# interfaces
.implements Lorg/vekendian/nexus/api/ModuleApi;


# direct methods
.method constructor <init>()V
    .registers 1

    .line 23
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public activity()Landroid/app/Activity;
    .registers 2

    .line 32
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->activity()Landroid/app/Activity;

    move-result-object v0

    return-object v0
.end method

.method public appVersion()Ljava/lang/String;
    .registers 5

    .line 63
    invoke-virtual {p0}, Lorg/vekendian/nexus/modules/ModuleApiImpl;->context()Landroid/content/Context;

    move-result-object v0

    const-string v1, "?"

    if-nez v0, :cond_9

    return-object v1

    .line 68
    :cond_9
    :try_start_9
    invoke-virtual {v0}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v2

    .line 69
    invoke-virtual {v0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v0

    const/4 v3, 0x0

    invoke-virtual {v2, v0, v3}, Landroid/content/pm/PackageManager;->getPackageInfo(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;

    move-result-object v0

    .line 70
    iget-object v2, v0, Landroid/content/pm/PackageInfo;->versionName:Ljava/lang/String;

    if-nez v2, :cond_1b

    goto :goto_1d

    :cond_1b
    iget-object v1, v0, Landroid/content/pm/PackageInfo;->versionName:Ljava/lang/String;
    :try_end_1d
    .catchall {:try_start_9 .. :try_end_1d} :catchall_1d

    :catchall_1d
    :goto_1d
    return-object v1
.end method

.method public context()Landroid/content/Context;
    .registers 2

    .line 27
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    return-object v0
.end method

.method public getModuleClassLoader(Ljava/lang/String;)Ljava/lang/ClassLoader;
    .registers 3

    .line 78
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->executor()Lorg/vekendian/nexus/api/NexusExecutor;

    move-result-object v0

    if-eqz v0, :cond_b

    .line 80
    invoke-interface {v0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->loadLibrary(Ljava/lang/String;)Ljava/lang/ClassLoader;

    move-result-object p1

    return-object p1

    :cond_b
    const/4 p1, 0x0

    return-object p1
.end method

.method public loadModule(Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 87
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->executor()Lorg/vekendian/nexus/api/NexusExecutor;

    move-result-object v0

    if-eqz v0, :cond_b

    .line 89
    invoke-interface {v0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->loadModule(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    return-object p1

    :cond_b
    const/4 p1, 0x0

    return-object p1
.end method

.method public log(Ljava/lang/String;)V
    .registers 3

    if-nez p1, :cond_4

    const-string p1, "(null)"

    :cond_4
    const-string v0, "NexusMod"

    .line 37
    invoke-static {v0, p1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method

.method public modulesChanged()V
    .registers 1

    .line 58
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->rerender()V

    return-void
.end method

.method public modulesDir()Ljava/lang/String;
    .registers 2

    .line 53
    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->modulesDir()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public toast(Ljava/lang/String;)V
    .registers 4

    if-nez p1, :cond_3

    return-void

    .line 48
    :cond_3
    invoke-virtual {p0}, Lorg/vekendian/nexus/modules/ModuleApiImpl;->context()Landroid/content/Context;

    move-result-object v0

    const/4 v1, 0x0

    invoke-static {v0, p1, v1}, Lorg/vekendian/nexus/modules/NexusToast;->show(Landroid/content/Context;Ljava/lang/String;I)V

    return-void
.end method
