.class final Lorg/vekendian/nexus/modules/LuaModules;
.super Ljava/lang/Object;
.source "LuaModules.java"


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

    .line 268
    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replace(CC)Ljava/lang/String;

    move-result-object p0

    const/16 v0, 0xa

    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replace(CC)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static find(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Lorg/vekendian/nexus/api/ModuleInfo;
    .registers 4

    .line 217
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->modules()Ljava/util/List;

    move-result-object p0

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p0

    :cond_8
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_1f

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lorg/vekendian/nexus/api/ModuleInfo;

    .line 218
    invoke-virtual {v0}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p1, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_8

    return-object v0

    :cond_1f
    const/4 p0, 0x0

    return-object p0
.end method

.method private static idOf(Ljava/lang/String;)Ljava/lang/String;
    .registers 3

    if-nez p0, :cond_5

    const-string p0, ""

    return-object p0

    :cond_5
    const/16 v0, 0x2f

    .line 250
    invoke-virtual {p0, v0}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v0

    if-ltz v0, :cond_13

    add-int/lit8 v0, v0, 0x1

    .line 251
    invoke-virtual {p0, v0}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object p0

    :cond_13
    const-string v0, ".lua"

    .line 252
    invoke-virtual {p0, v0}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_2d

    const-string v0, ".jar"

    invoke-virtual {p0, v0}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_2d

    const-string v0, ".dex"

    .line 253
    invoke-virtual {p0, v0}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_2c

    goto :goto_2d

    :cond_2c
    return-object p0

    :cond_2d
    :goto_2d
    const/4 v0, 0x0

    .line 254
    invoke-virtual {p0}, Ljava/lang/String;->length()I

    move-result v1

    add-int/lit8 v1, v1, -0x4

    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static install(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 10

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x0

    const/4 v6, 0x0

    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    .line 45
    invoke-static/range {v0 .. v6}, Lorg/vekendian/nexus/modules/LuaModules;->install(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method static install(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;
    .registers 16

    .line 52
    new-instance v0, Ljava/io/File;

    invoke-direct {v0, p2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 53
    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result v1

    if-eqz v1, :cond_33

    invoke-virtual {v0}, Ljava/io/File;->canRead()Z

    move-result v1

    if-nez v1, :cond_12

    goto :goto_33

    .line 58
    :cond_12
    :try_start_12
    invoke-static {p5}, Lorg/vekendian/nexus/modules/LuaModules;->parseVersion(Ljava/lang/String;)I

    move-result v7
    :try_end_16
    .catch Ljava/lang/NumberFormatException; {:try_start_12 .. :try_end_16} :catch_30

    .line 63
    :try_start_16
    invoke-static {v0}, Landroid/net/Uri;->fromFile(Ljava/io/File;)Landroid/net/Uri;

    move-result-object v4

    move-object v2, p1

    move-object v3, p0

    move-object v5, p3

    move-object v6, p4

    move-object v8, p6

    invoke-interface/range {v2 .. v8}, Lorg/vekendian/nexus/api/NexusExecutor;->add(Landroid/content/Context;Landroid/net/Uri;Ljava/lang/String;Ljava/lang/String;ILjava/lang/String;)Ljava/lang/String;

    move-result-object p0

    if-nez p0, :cond_28

    const-string p0, "module could not be imported (expected .lua, .jar or .dex)"
    :try_end_27
    .catchall {:try_start_16 .. :try_end_27} :catchall_2a

    goto :goto_29

    :cond_28
    const/4 p0, 0x0

    :goto_29
    return-object p0

    :catchall_2a
    move-exception p0

    .line 69
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :catch_30
    const-string p0, "version must be an integer"

    return-object p0

    .line 54
    :cond_33
    :goto_33
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "cannot read "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static installBytes(Landroid/content/Context;Lorg/vekendian/nexus/api/NexusExecutor;[BLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;
    .registers 15

    if-eqz p2, :cond_24

    .line 77
    array-length v0, p2

    if-nez v0, :cond_6

    goto :goto_24

    .line 82
    :cond_6
    :try_start_6
    invoke-static {p5}, Lorg/vekendian/nexus/modules/LuaModules;->parseVersion(Ljava/lang/String;)I

    move-result v6
    :try_end_a
    .catch Ljava/lang/NumberFormatException; {:try_start_6 .. :try_end_a} :catch_21

    move-object v1, p1

    move-object v2, p0

    move-object v3, p2

    move-object v4, p3

    move-object v5, p4

    move-object v7, p6

    .line 87
    :try_start_10
    invoke-interface/range {v1 .. v7}, Lorg/vekendian/nexus/api/NexusExecutor;->addBytes(Landroid/content/Context;[BLjava/lang/String;Ljava/lang/String;ILjava/lang/String;)Ljava/lang/String;

    move-result-object p0

    if-nez p0, :cond_19

    const-string p0, "module could not be imported"
    :try_end_18
    .catchall {:try_start_10 .. :try_end_18} :catchall_1b

    goto :goto_1a

    :cond_19
    const/4 p0, 0x0

    :goto_1a
    return-object p0

    :catchall_1b
    move-exception p0

    .line 91
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :catch_21
    const-string p0, "version must be an integer"

    return-object p0

    :cond_24
    :goto_24
    const-string p0, "empty module content"

    return-object p0
.end method

.method static invoke(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 6

    const/16 v0, 0x9

    .line 154
    invoke-virtual {p1, v0}, Ljava/lang/String;->indexOf(I)I

    move-result v1

    const/4 v2, -0x1

    if-gez v1, :cond_b

    const/4 v3, -0x1

    goto :goto_11

    :cond_b
    add-int/lit8 v3, v1, 0x1

    .line 155
    invoke-virtual {p1, v0, v3}, Ljava/lang/String;->indexOf(II)I

    move-result v3

    :goto_11
    if-gez v3, :cond_14

    goto :goto_1a

    :cond_14
    add-int/lit8 v2, v3, 0x1

    .line 156
    invoke-virtual {p1, v0, v2}, Ljava/lang/String;->indexOf(II)I

    move-result v2

    :goto_1a
    if-ltz v1, :cond_59

    if-ltz v3, :cond_59

    if-gez v2, :cond_21

    goto :goto_59

    :cond_21
    const/4 v0, 0x0

    .line 160
    invoke-virtual {p1, v0, v1}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v0

    add-int/lit8 v1, v1, 0x1

    .line 161
    invoke-virtual {p1, v1, v3}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v1

    add-int/lit8 v2, v2, 0x1

    .line 162
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v3

    invoke-virtual {p1, v2, v3}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object p1

    .line 163
    invoke-static {p0, v0}, Lorg/vekendian/nexus/modules/LuaModules;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_4e

    .line 164
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "no module at "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 167
    :cond_4e
    :try_start_4e
    invoke-interface {p0, v0, v1, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->jarInvoke(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_52
    .catchall {:try_start_4e .. :try_end_52} :catchall_53

    return-object p0

    :catchall_53
    move-exception p0

    .line 169
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

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

    .line 192
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v1

    if-nez v1, :cond_a

    goto :goto_4f

    .line 195
    :cond_a
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->modules()Ljava/util/List;

    move-result-object p0

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p0

    :cond_12
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_4f

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lorg/vekendian/nexus/api/ModuleInfo;

    .line 196
    invoke-virtual {v1}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    const/4 v3, 0x1

    if-eqz v2, :cond_2a

    return v3

    .line 199
    :cond_2a
    invoke-virtual {v1}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0x2f

    .line 200
    invoke-virtual {v1, v2}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v2

    if-ltz v2, :cond_3c

    add-int/lit8 v2, v2, 0x1

    .line 202
    invoke-virtual {v1, v2}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    :cond_3c
    const/16 v2, 0x2e

    .line 204
    invoke-virtual {v1, v2}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v2

    if-lez v2, :cond_48

    .line 206
    invoke-virtual {v1, v0, v2}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v1

    .line 208
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
    invoke-interface {p0}, Lorg/vekendian/nexus/api/NexusExecutor;->modules()Ljava/util/List;

    move-result-object p0

    .line 31
    invoke-interface {p0}, Ljava/util/List;->size()I

    move-result v0

    new-array v1, v0, [Ljava/lang/String;

    const/4 v2, 0x0

    :goto_b
    if-ge v2, v0, :cond_a2

    .line 33
    invoke-interface {p0, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Lorg/vekendian/nexus/api/ModuleInfo;

    .line 34
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5}, Lorg/vekendian/nexus/modules/LuaModules;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v5, 0x9

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->name()Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 35
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->idOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->state()I

    move-result v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->state(I)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 36
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->version()I

    move-result v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->autostart()Z

    move-result v6

    if-eqz v6, :cond_69

    const-string v6, "true"

    goto :goto_6b

    :cond_69
    const-string v6, "false"

    :goto_6b
    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 37
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->type()Lorg/vekendian/nexus/api/ModuleInfo$Type;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->type(Lorg/vekendian/nexus/api/ModuleInfo$Type;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->description()Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lorg/vekendian/nexus/modules/LuaModules;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    .line 38
    invoke-virtual {v3}, Lorg/vekendian/nexus/api/ModuleInfo;->message()Ljava/lang/String;

    move-result-object v3

    invoke-static {v3}, Lorg/vekendian/nexus/modules/LuaModules;->field(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    aput-object v3, v1, v2

    add-int/lit8 v2, v2, 0x1

    goto/16 :goto_b

    :cond_a2
    return-object v1
.end method

.method static loader(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 136
    invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaModules;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_8

    const/4 p0, 0x0

    return-object p0

    .line 140
    :cond_8
    :try_start_8
    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->loadLibrary(Ljava/lang/String;)Ljava/lang/ClassLoader;

    move-result-object p0
    :try_end_c
    .catchall {:try_start_8 .. :try_end_c} :catchall_d

    return-object p0

    :catchall_d
    move-exception p0

    .line 142
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method private static parseVersion(Ljava/lang/String;)I
    .registers 2

    if-eqz p0, :cond_16

    .line 97
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v0

    if-nez v0, :cond_d

    goto :goto_16

    .line 100
    :cond_d
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result p0

    return p0

    :cond_16
    :goto_16
    const/4 p0, 0x0

    return p0
.end method

.method static source(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 180
    invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaModules;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_18

    .line 181
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "no module at "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 184
    :cond_18
    :try_start_18
    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->luaSource(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_1c
    .catchall {:try_start_18 .. :try_end_1c} :catchall_1d

    return-object p0

    :catchall_1d
    move-exception p0

    .line 186
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static spec(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Ljava/lang/Object;
    .registers 3

    .line 114
    invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaModules;->known(Lorg/vekendian/nexus/api/NexusExecutor;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_18

    .line 115
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "no module at "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 118
    :cond_18
    :try_start_18
    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->jarSpec(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0
    :try_end_1c
    .catchall {:try_start_18 .. :try_end_1c} :catchall_1d

    return-object p0

    :catchall_1d
    move-exception p0

    .line 120
    invoke-static {p0}, Lorg/vekendian/nexus/modules/ModuleLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

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

.method private static type(Lorg/vekendian/nexus/api/ModuleInfo$Type;)Ljava/lang/String;
    .registers 1

    if-nez p0, :cond_5

    const-string p0, "lua"

    goto :goto_d

    .line 260
    :cond_5
    invoke-virtual {p0}, Lorg/vekendian/nexus/api/ModuleInfo$Type;->name()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;

    move-result-object p0

    :goto_d
    return-object p0
.end method

.method static uninstall(Lorg/vekendian/nexus/api/NexusExecutor;Lorg/vekendian/nexus/api/ModuleInfo;)Z
    .registers 2

    .line 226
    invoke-virtual {p1}, Lorg/vekendian/nexus/api/ModuleInfo;->path()Ljava/lang/String;

    move-result-object p1

    invoke-interface {p0, p1}, Lorg/vekendian/nexus/api/NexusExecutor;->remove(Ljava/lang/String;)Z

    move-result p0

    return p0
.end method
