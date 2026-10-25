.class public final Lorg/vekendian/nexus/extensions/LuaBridge;
.super Ljava/lang/Object;
.source "LuaBridge.java"


# static fields
.field static final ERROR_NOT_RUNNING:Ljava/lang/String; = "extension system is not running"


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 34
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static call(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;
    .registers 5

    if-nez p1, :cond_5

    const-string p0, "unknown function"

    return-object p0

    :cond_5
    const/16 v0, 0x2e

    .line 114
    invoke-virtual {p1, v0}, Ljava/lang/String;->indexOf(I)I

    move-result v0

    if-gtz v0, :cond_1f

    .line 116
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "unknown function: nexus."

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_1f
    const/4 v1, 0x0

    .line 118
    invoke-virtual {p1, v1, v0}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p0, p1, p2}, Lorg/vekendian/nexus/extensions/LuaBridge;->callCategory(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method static callCategory(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;
    .registers 5

    const-string v0, "extensions"

    .line 45
    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_d

    .line 46
    invoke-static {p1, p2, p3}, Lorg/vekendian/nexus/extensions/LuaBridge;->callExtensions(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0

    .line 48
    :cond_d
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "unknown function: nexus."

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static callExtensions(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;
    .registers 7

    .line 52
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object p0

    .line 53
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->executor()Lorg/vekendian/nexus/api/NexusExecutor;

    move-result-object v0

    if-eqz p0, :cond_b3

    if-nez v0, :cond_e

    goto/16 :goto_b3

    :cond_e
    const/16 v1, 0xb

    .line 58
    :try_start_10
    invoke-virtual {p1, v1}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    const-string v2, "list"

    .line 59
    invoke-virtual {v2, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_21

    .line 60
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/LuaExtensions;->list(Lorg/vekendian/nexus/api/NexusExecutor;)[Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_21
    if-nez p2, :cond_26

    const-string v2, ""

    goto :goto_2a

    .line 62
    :cond_26
    invoke-virtual {p2}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v2

    .line 63
    :goto_2a
    invoke-virtual {v2}, Ljava/lang/String;->length()I

    move-result v3

    if-eqz v3, :cond_aa

    const-string v3, "nil"

    invoke-virtual {v3, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_39

    goto :goto_aa

    :cond_39
    const-string v3, "install"

    .line 66
    invoke-virtual {v3, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_46

    .line 67
    invoke-static {p0, v0, v2}, Lorg/vekendian/nexus/extensions/LuaExtensions;->install(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0

    :cond_46
    const-string p0, "spec"

    .line 71
    invoke-virtual {p0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_53

    .line 72
    invoke-static {v0, v2}, Lorg/vekendian/nexus/extensions/LuaExtensions;->spec(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0

    :cond_53
    const-string p0, "invoke"

    .line 74
    invoke-virtual {p0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_60

    .line 77
    invoke-static {v0, p2}, Lorg/vekendian/nexus/extensions/LuaExtensions;->invoke(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0

    :cond_60
    const-string p0, "source"

    .line 79
    invoke-virtual {p0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_6d

    .line 80
    invoke-static {v0, v2}, Lorg/vekendian/nexus/extensions/LuaExtensions;->source(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0

    .line 82
    :cond_6d
    invoke-static {v0, v2}, Lorg/vekendian/nexus/extensions/LuaExtensions;->find(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Lorg/vekendian/nexus/api/ExtensionInfo;

    move-result-object p0

    if-nez p0, :cond_85

    .line 84
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "no extension at "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_85
    const-string p2, "uninstall"

    .line 86
    invoke-virtual {p2, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_98

    .line 87
    invoke-static {v0, p0}, Lorg/vekendian/nexus/extensions/LuaExtensions;->uninstall(Lorg/vekendian/nexus/api/NexusExecutor;Lorg/vekendian/nexus/api/ExtensionInfo;)Z

    move-result p0

    if-eqz p0, :cond_95

    const/4 p0, 0x0

    goto :goto_97

    :cond_95
    const-string p0, "extension could not be removed"

    :goto_97
    return-object p0

    .line 90
    :cond_98
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "unknown function: nexus."

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_aa
    :goto_aa
    const-string p0, "missing extension path"
    :try_end_ac
    .catchall {:try_start_10 .. :try_end_ac} :catchall_ad

    return-object p0

    :catchall_ad
    move-exception p0

    .line 92
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_b3
    :goto_b3
    const-string p0, "extension system is not running"

    return-object p0
.end method

.method public static capabilities()[Ljava/lang/String;
    .registers 1

    .line 143
    sget-object v0, Lorg/vekendian/nexus/extensions/PermRules;->CAPABILITIES:[Ljava/lang/String;

    invoke-virtual {v0}, [Ljava/lang/String;->clone()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, [Ljava/lang/String;

    return-object v0
.end method

.method public static clearRemembered()V
    .registers 1

    .line 179
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_9

    .line 181
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/LuaPerms;->clearRemembered(Landroid/content/Context;)V

    :cond_9
    return-void
.end method

.method public static global(Ljava/lang/String;)Z
    .registers 2

    .line 147
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_e

    .line 148
    invoke-static {v0, p0}, Lorg/vekendian/nexus/extensions/LuaPerms;->global(Landroid/content/Context;Ljava/lang/String;)Z

    move-result p0

    if-eqz p0, :cond_e

    const/4 p0, 0x1

    goto :goto_f

    :cond_e
    const/4 p0, 0x0

    :goto_f
    return p0
.end method

.method public static migrateBroadGrants()V
    .registers 1

    .line 172
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_9

    .line 174
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/LuaPerms;->migrateBroadGrants(Landroid/content/Context;)V

    :cond_9
    return-void
.end method

.method public static permMessage(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .registers 7

    .line 191
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-nez v0, :cond_7

    return-object p2

    .line 195
    :cond_7
    new-instance v1, Ljava/io/File;

    const-string v2, ""

    if-nez p1, :cond_f

    move-object v3, v2

    goto :goto_10

    :cond_f
    move-object v3, p1

    :goto_10
    invoke-direct {v1, v3}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v1

    .line 196
    invoke-virtual {v1}, Ljava/lang/String;->length()I

    move-result v3

    if-nez v3, :cond_21

    if-nez p1, :cond_20

    move-object p1, v2

    :cond_20
    move-object v1, p1

    .line 199
    :cond_21
    invoke-virtual {v0, p0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object p0

    const/4 p1, 0x2

    new-array p1, p1, [Ljava/lang/Object;

    const/4 v0, 0x0

    aput-object v1, p1, v0

    const/4 v0, 0x1

    aput-object p2, p1, v0

    invoke-static {p0, p1}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method public static policy(Ljava/lang/String;Ljava/lang/String;)I
    .registers 3

    .line 125
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-nez v0, :cond_8

    const/4 p0, 0x0

    return p0

    .line 129
    :cond_8
    invoke-static {v0, p0, p1}, Lorg/vekendian/nexus/extensions/LuaPerms;->allowed(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Z

    move-result p0

    return p0
.end method

.method public static ready()Z
    .registers 1

    .line 100
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_e

    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->executor()Lorg/vekendian/nexus/api/NexusExecutor;

    move-result-object v0

    if-eqz v0, :cond_e

    const/4 v0, 0x1

    goto :goto_f

    :cond_e
    const/4 v0, 0x0

    :goto_f
    return v0
.end method

.method public static remember(Ljava/lang/String;Ljava/lang/String;)V
    .registers 3

    .line 135
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_9

    .line 137
    invoke-static {v0, p0, p1}, Lorg/vekendian/nexus/extensions/LuaPerms;->remember(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V

    :cond_9
    return-void
.end method

.method public static scriptOverride(Ljava/lang/String;)Z
    .registers 2

    .line 166
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_e

    .line 167
    invoke-static {v0, p0}, Lorg/vekendian/nexus/extensions/LuaPerms;->anyScriptOverride(Landroid/content/Context;Ljava/lang/String;)Z

    move-result p0

    if-eqz p0, :cond_e

    const/4 p0, 0x1

    goto :goto_f

    :cond_e
    const/4 p0, 0x0

    :goto_f
    return p0
.end method

.method public static setGlobal(Ljava/lang/String;Z)V
    .registers 3

    .line 152
    invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->app()Landroid/content/Context;

    move-result-object v0

    if-eqz v0, :cond_9

    .line 154
    invoke-static {v0, p0, p1}, Lorg/vekendian/nexus/extensions/LuaPerms;->setGlobal(Landroid/content/Context;Ljava/lang/String;Z)V

    :cond_9
    return-void
.end method
