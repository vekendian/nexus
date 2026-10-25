.class final Lorg/vekendian/nexus/extensions/LuaExtensions;
.super Ljava/lang/Object;
.source "LuaExtensions.java"


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 26
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static field(Ljava/lang/String;)Ljava/lang/String;
    .registers 3

    if-nez p0, :cond_5

    const-string p0, ""

    return-object p0

    :cond_5
    const/16 v0, 0x9

    const/16 v1, 0x20

    .line 182
    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replace(CC)Ljava/lang/String;

    move-result-object p0

    const/16 v0, 0xa

    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replace(CC)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static find(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Lorg/vekendian/nexus/api/ExtensionInfo;
    .registers 4

    .line 149
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->extensions()Ljava/util/List;

    move-result-object p0

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p0

    :cond_8
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_1f

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lorg/vekendian/nexus/api/ExtensionInfo;

    .line 150
    invoke-virtual {v0}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p1, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_8

    return-object v0

    :cond_1f
    const/4 p0, 0x0

    return-object p0
.end method

.method static install(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 5

    .line 43
    new-instance v0, Ljava/io/File;

    invoke-direct {v0, p2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 44
    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result v1

    if-eqz v1, :cond_27

    invoke-virtual {v0}, Ljava/io/File;->canRead()Z

    move-result v1

    if-nez v1, :cond_12

    goto :goto_27

    .line 48
    :cond_12
    :try_start_12
    invoke-static {v0}, Landroid/net/Uri;->fromFile(Ljava/io/File;)Landroid/net/Uri;

    move-result-object p2

    invoke-interface {p1, p0, p2}, Lorg/vekendian/nexus/api/NexusExecutor;->add(Landroid/content/Context;Landroid/net/Uri;)Ljava/lang/String;

    move-result-object p0

    if-nez p0, :cond_1f

    const-string p0, "extension could not be imported (not a loadable jar?)"
    :try_end_1e
    .catchall {:try_start_12 .. :try_end_1e} :catchall_21

    goto :goto_20

    :cond_1f
    const/4 p0, 0x0

    :goto_20
    return-object p0

    :catchall_21
    move-exception p0

    .line 53
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 45
    :cond_27
    :goto_27
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "cannot read "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static invoke(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 6

    const/16 v0, 0x9

    .line 86
    invoke-virtual {p1, v0}, Ljava/lang/String;->indexOf(I)I

    move-result v1

    const/4 v2, -0x1

    if-gez v1, :cond_b

    const/4 v3, -0x1

    goto :goto_11

    :cond_b
    add-int/lit8 v3, v1, 0x1

    .line 87
    invoke-virtual {p1, v0, v3}, Ljava/lang/String;->indexOf(II)I

    move-result v3

    :goto_11
    if-gez v3, :cond_14

    goto :goto_1a

    :cond_14
    add-int/lit8 v2, v3, 0x1

    .line 88
    invoke-virtual {p1, v0, v2}, Ljava/lang/String;->indexOf(II)I

    move-result v2

    :goto_1a
    if-ltz v1, :cond_59

    if-ltz v3, :cond_59

    if-gez v2, :cond_21

    goto :goto_59

    :cond_21
    const/4 v0, 0x0

    .line 92
    invoke-virtual {p1, v0, v1}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v0

    add-int/lit8 v1, v1, 0x1

    .line 93
    invoke-virtual {p1, v1, v3}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v1

    add-int/lit8 v2, v2, 0x1

    .line 94
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v3

    invoke-virtual {p1, v2, v3}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object p1

    .line 95
    invoke-static {p0, v0}, Lorg/vekendian/nexus/extensions/LuaExtensions;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_4e

    .line 96
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "no extension at "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 99
    :cond_4e
    :try_start_4e
    invoke-interface {p0, v0, v1, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->jarInvoke(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_52
    .catchall {:try_start_4e .. :try_end_52} :catchall_53

    return-object p0

    :catchall_53
    move-exception p0

    .line 101
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_59
    :goto_59
    const-string p0, "malformed invoke record"

    return-object p0
.end method

.method private static known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z
    .registers 6

    const/4 v0, 0x0

    if-eqz p1, :cond_4f

    .line 124
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v1

    if-nez v1, :cond_a

    goto :goto_4f

    .line 127
    :cond_a
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->extensions()Ljava/util/List;

    move-result-object p0

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p0

    :cond_12
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_4f

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lorg/vekendian/nexus/api/ExtensionInfo;

    .line 128
    invoke-virtual {v1}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    const/4 v3, 0x1

    if-eqz v2, :cond_2a

    return v3

    .line 131
    :cond_2a
    invoke-virtual {v1}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0x2f

    .line 132
    invoke-virtual {v1, v2}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v2

    if-ltz v2, :cond_3c

    add-int/lit8 v2, v2, 0x1

    .line 134
    invoke-virtual {v1, v2}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    :cond_3c
    const/16 v2, 0x2e

    .line 136
    invoke-virtual {v1, v2}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v2

    if-lez v2, :cond_48

    .line 138
    invoke-virtual {v1, v0, v2}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v1

    .line 140
    :cond_48
    invoke-virtual {p1, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_12

    return v3

    :cond_4f
    :goto_4f
    return v0
.end method

.method static list(Lorg/vekendian/nexus/api/NexusExecutor;)[Ljava/lang/String;
    .registers 8

    .line 30
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->extensions()Ljava/util/List;

    move-result-object p0

    .line 31
    invoke-interface {p0}, Ljava/util/List;->size()I

    move-result v0

    new-array v1, v0, [Ljava/lang/String;

    const/4 v2, 0x0

    :goto_b
    if-ge v2, v0, :cond_65

    .line 33
    invoke-interface {p0, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Lorg/vekendian/nexus/api/ExtensionInfo;

    .line 34
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/extensions/LuaExtensions;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v5, 0x9

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ExtensionInfo;->name()Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/extensions/LuaExtensions;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 35
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ExtensionInfo;->state()I

    move-result v6

    invoke-static {v6}, Lorg/vekendian/nexus/extensions/LuaExtensions;->state(I)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ExtensionInfo;->version()I

    move-result v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 36
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ExtensionInfo;->autostart()Z

    move-result v3

    if-eqz v3, :cond_57

    const-string v3, "true"

    goto :goto_59

    :cond_57
    const-string v3, "false"

    :goto_59
    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    aput-object v3, v1, v2

    add-int/lit8 v2, v2, 0x1

    goto :goto_b

    :cond_65
    return-object v1
.end method

.method static source(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 112
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/LuaExtensions;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_18

    .line 113
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "no extension at "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 116
    :cond_18
    :try_start_18
    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->luaSource(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_1c
    .catchall {:try_start_18 .. :try_end_1c} :catchall_1d

    return-object p0

    :catchall_1d
    move-exception p0

    .line 118
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static spec(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 68
    invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/LuaExtensions;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_18

    .line 69
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "no extension at "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 72
    :cond_18
    :try_start_18
    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->jarSpec(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_1c
    .catchall {:try_start_18 .. :try_end_1c} :catchall_1d

    return-object p0

    :catchall_1d
    move-exception p0

    .line 74
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static state(I)Ljava/lang/String;
    .registers 2

    const/4 v0, 0x1

    if-eq p0, v0, :cond_18

    const/4 v0, 0x2

    if-eq p0, v0, :cond_15

    const/4 v0, 0x3

    if-eq p0, v0, :cond_12

    const/4 v0, 0x4

    if-eq p0, v0, :cond_f

    const-string p0, "idle"

    return-object p0

    :cond_f
    const-string p0, "error"

    return-object p0

    :cond_12
    const-string p0, "stopped"

    return-object p0

    :cond_15
    const-string p0, "finished"

    return-object p0

    :cond_18
    const-string p0, "running"

    return-object p0
.end method

.method static uninstall(Lorg/vekendian/nexus/api/NexusExecutor;Lorg/vekendian/nexus/api/ExtensionInfo;)Z
    .registers 2

    .line 158
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ExtensionInfo;->path()Ljava/lang/String;

    move-result-object p1

    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->remove(Ljava/lang/String;)Z

    move-result p0

    return p0
.end method
