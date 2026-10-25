.class final Lorg/vekendian/nexus/extensions/ExtensionLoader;
.super Ljava/lang/Object;
.source "ExtensionLoader.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;
    }
.end annotation


# static fields
.field private static final ASSET_DIR:Ljava/lang/String; = "dexexec"

.field private static final ASSET_NAME:Ljava/lang/String; = "nexus_dexexec.dex"

.field static final ENTRIES:[Ljava/lang/String;

.field private static final STATE_KEY:Ljava/lang/String; = "length"

.field private static final STATE_PREFS:Ljava/lang/String; = "nexus_dexexec_asset"


# direct methods
.method static constructor <clinit>()V
    .registers 1

    const-string v0, "nexus.ExtensionRegistry"

    .line 51
    filled-new-array {v0}, [Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lorg/vekendian/nexus/extensions/ExtensionLoader;->ENTRIES:[Ljava/lang/String;

    return-void
.end method

.method private constructor <init>()V
    .registers 1

    .line 62
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static call(Ljava/lang/Object;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;[Ljava/lang/String;)V
    .registers 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/Object;",
            "Ljava/lang/String;",
            "[",
            "Ljava/lang/Class<",
            "*>;[",
            "Ljava/lang/Object;",
            "[",
            "Ljava/lang/String;",
            ")V"
        }
    .end annotation

    if-nez p0, :cond_3

    return-void

    .line 227
    :cond_3
    :try_start_3
    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-virtual {v0, p1, p2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object p2

    .line 228
    invoke-virtual {p2, p0, p3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_e
    .catch Ljava/lang/NoSuchMethodException; {:try_start_3 .. :try_end_e} :catch_30
    .catchall {:try_start_3 .. :try_end_e} :catchall_f

    goto :goto_30

    :catchall_f
    move-exception p0

    const/4 p2, 0x0

    .line 232
    new-instance p3, Ljava/lang/StringBuilder;

    invoke-direct {p3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p1, "() failed: "

    invoke-virtual {p3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p3, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    aput-object p0, p4, p2

    const-string p1, "NexusMod"

    .line 233
    invoke-static {p1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    :catch_30
    :goto_30
    return-void
.end method

.method static close(Ljava/io/Closeable;)V
    .registers 1

    if-nez p0, :cond_3

    return-void

    .line 281
    :cond_3
    :try_start_3
    invoke-interface {p0}, Ljava/io/Closeable;->close()V
    :try_end_6
    .catch Ljava/io/IOException; {:try_start_3 .. :try_end_6} :catch_6

    :catch_6
    return-void
.end method

.method static closeQuietly(Ljava/lang/Object;)V
    .registers 2

    .line 266
    instance-of v0, p0, Ljava/io/Closeable;

    if-nez v0, :cond_5

    return-void

    .line 270
    :cond_5
    :try_start_5
    check-cast p0, Ljava/io/Closeable;

    invoke-interface {p0}, Ljava/io/Closeable;->close()V
    :try_end_a
    .catchall {:try_start_5 .. :try_end_a} :catchall_a

    :catchall_a
    return-void
.end method

.method static delete(Ljava/io/File;)V
    .registers 1

    if-eqz p0, :cond_5

    .line 200
    invoke-virtual {p0}, Ljava/io/File;->delete()Z

    :cond_5
    return-void
.end method

.method static describe(Ljava/lang/Throwable;)Ljava/lang/String;
    .registers 3

    if-nez p0, :cond_5

    const-string p0, "?"

    return-object p0

    .line 241
    :cond_5
    invoke-virtual {p0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_11

    .line 242
    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v1

    if-nez v1, :cond_19

    :cond_11
    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v0

    :cond_19
    return-object v0
.end method

.method static extract(Landroid/content/Context;I)Ljava/io/File;
    .registers 19

    move-object/from16 v0, p0

    move/from16 v1, p1

    const/4 v2, 0x0

    if-eqz v0, :cond_13a

    if-nez v1, :cond_b

    goto/16 :goto_13a

    :cond_b
    const-string v3, "dexexec"

    const/4 v4, 0x0

    .line 74
    invoke-virtual {v0, v3, v4}, Landroid/content/Context;->getDir(Ljava/lang/String;I)Ljava/io/File;

    move-result-object v3

    .line 75
    invoke-virtual {v3}, Ljava/io/File;->isDirectory()Z

    move-result v5

    const-string v6, "NexusMod"

    if-nez v5, :cond_35

    invoke-virtual {v3}, Ljava/io/File;->mkdirs()Z

    move-result v5

    if-nez v5, :cond_35

    .line 76
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "asset dir not created: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v6, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-object v2

    .line 79
    :cond_35
    new-instance v5, Ljava/io/File;

    const-string v7, "nexus_dexexec.dex"

    invoke-direct {v5, v3, v7}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    const-string v7, "nexus_dexexec_asset"

    .line 80
    invoke-virtual {v0, v7, v4}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v7

    const-wide/16 v8, -0x1

    const-string v10, "length"

    .line 81
    invoke-interface {v7, v10, v8, v9}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v8

    .line 85
    :try_start_4a
    invoke-virtual/range {p0 .. p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0, v1}, Landroid/content/res/Resources;->openRawResource(I)Ljava/io/InputStream;

    move-result-object v1

    .line 86
    invoke-virtual {v1}, Ljava/io/InputStream;->available()I
    :try_end_55
    .catchall {:try_start_4a .. :try_end_55} :catchall_123

    .line 95
    new-instance v11, Ljava/io/File;

    const-string v0, "nexus_dexexec.dex.part"

    invoke-direct {v11, v3, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 99
    :try_start_5c
    new-instance v3, Ljava/io/FileOutputStream;

    invoke-direct {v3, v11}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_61
    .catchall {:try_start_5c .. :try_end_61} :catchall_102

    const/16 v0, 0x2000

    :try_start_63
    new-array v0, v0, [B

    const-wide/16 v12, 0x0

    move-wide v14, v12

    .line 102
    :goto_68
    invoke-virtual {v1, v0}, Ljava/io/InputStream;->read([B)I

    move-result v2

    if-lez v2, :cond_79

    .line 103
    invoke-virtual {v3, v0, v4, v2}, Ljava/io/FileOutputStream;->write([BII)V

    move-object/from16 v16, v5

    int-to-long v4, v2

    add-long/2addr v14, v4

    move-object/from16 v5, v16

    const/4 v4, 0x0

    goto :goto_68

    :cond_79
    move-object/from16 v16, v5

    .line 106
    invoke-virtual {v3}, Ljava/io/FileOutputStream;->flush()V

    .line 107
    invoke-virtual {v3}, Ljava/io/FileOutputStream;->getFD()Ljava/io/FileDescriptor;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/FileDescriptor;->sync()V
    :try_end_85
    .catchall {:try_start_63 .. :try_end_85} :catchall_100

    .line 115
    invoke-static {v3}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->close(Ljava/io/Closeable;)V

    .line 116
    invoke-static {v1}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->close(Ljava/io/Closeable;)V

    cmp-long v0, v14, v12

    if-nez v0, :cond_94

    .line 118
    invoke-static {v11}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->delete(Ljava/io/File;)V

    :goto_92
    const/4 v1, 0x0

    return-object v1

    .line 121
    :cond_94
    invoke-virtual/range {v16 .. v16}, Ljava/io/File;->isFile()Z

    move-result v0

    if-eqz v0, :cond_aa

    invoke-virtual/range {v16 .. v16}, Ljava/io/File;->length()J

    move-result-wide v0

    cmp-long v2, v0, v14

    if-nez v2, :cond_aa

    cmp-long v0, v8, v14

    if-nez v0, :cond_aa

    .line 124
    invoke-static {v11}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->delete(Ljava/io/File;)V

    return-object v16

    :cond_aa
    move-object/from16 v0, v16

    .line 127
    invoke-virtual {v11, v0}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result v1

    if-nez v1, :cond_d3

    .line 130
    invoke-static {v0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->delete(Ljava/io/File;)V

    .line 131
    invoke-virtual {v11, v0}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result v1

    if-nez v1, :cond_d3

    .line 132
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "asset rename failed: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v6, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 133
    invoke-static {v11}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->delete(Ljava/io/File;)V

    goto :goto_92

    .line 137
    :cond_d3
    invoke-interface {v7}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1, v10, v14, v15}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->commit()Z

    .line 138
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "asset extracted: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    const-string v2, " ("

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v14, v15}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    const-string v2, " bytes)"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v6, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-object v0

    :catchall_100
    move-exception v0

    goto :goto_104

    :catchall_102
    move-exception v0

    const/4 v3, 0x0

    .line 109
    :goto_104
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "asset copy failed: "

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v6, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 110
    invoke-static {v3}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->close(Ljava/io/Closeable;)V

    .line 111
    invoke-static {v1}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->close(Ljava/io/Closeable;)V

    .line 112
    invoke-static {v11}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->delete(Ljava/io/File;)V

    goto/16 :goto_92

    :catchall_123
    move-exception v0

    .line 88
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "asset open failed: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v6, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    goto/16 :goto_92

    :cond_13a
    :goto_13a
    move-object v1, v2

    return-object v1
.end method

.method static join([Ljava/lang/String;)Ljava/lang/String;
    .registers 4

    .line 247
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const/4 v1, 0x0

    .line 248
    :goto_6
    array-length v2, p0

    if-ge v1, v2, :cond_18

    if-lez v1, :cond_10

    const-string v2, ", "

    .line 250
    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 252
    :cond_10
    aget-object v2, p0, v1

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    add-int/lit8 v1, v1, 0x1

    goto :goto_6

    .line 254
    :cond_18
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static load(Landroid/content/Context;Ljava/lang/ClassLoader;Ljava/io/File;Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;[Ljava/lang/String;)Ljava/lang/Object;
    .registers 9

    const/4 v0, 0x0

    const/4 v1, 0x0

    .line 150
    :try_start_2
    new-instance v2, Ldalvik/system/DexClassLoader;

    .line 151
    invoke-virtual {p2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object p2

    .line 152
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->optimizedDir(Landroid/content/Context;)Ljava/lang/String;

    move-result-object p0

    invoke-direct {v2, p2, p0, v1, p1}, Ldalvik/system/DexClassLoader;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)V
    :try_end_f
    .catchall {:try_start_2 .. :try_end_f} :catchall_4e

    .line 156
    :try_start_f
    sget-object p0, Lorg/vekendian/nexus/extensions/ExtensionLoader;->ENTRIES:[Ljava/lang/String;

    array-length p1, p0

    const/4 p2, 0x0

    :goto_13
    if-ge p2, p1, :cond_1f

    aget-object v3, p0, p2
    :try_end_17
    .catchall {:try_start_f .. :try_end_17} :catchall_4c

    .line 158
    :try_start_17
    invoke-virtual {v2, v3}, Ljava/lang/ClassLoader;->loadClass(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object p0
    :try_end_1b
    .catch Ljava/lang/ClassNotFoundException; {:try_start_17 .. :try_end_1b} :catch_1c
    .catchall {:try_start_17 .. :try_end_1b} :catchall_4c

    goto :goto_20

    :catch_1c
    add-int/lit8 p2, p2, 0x1

    goto :goto_13

    :cond_1f
    move-object p0, v1

    :goto_20
    if-nez p0, :cond_44

    .line 165
    :try_start_22
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "no entry class (looked for "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object p1, Lorg/vekendian/nexus/extensions/ExtensionLoader;->ENTRIES:[Ljava/lang/String;

    invoke-static {p1}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->join([Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p1, ")"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    aput-object p0, p4, v0

    .line 166
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->closeQuietly(Ljava/lang/Object;)V

    return-object v1

    .line 169
    :cond_44
    invoke-static {p0, p3}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->readMeta(Ljava/lang/Class;Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;)V

    .line 173
    invoke-virtual {p0}, Ljava/lang/Class;->newInstance()Ljava/lang/Object;

    move-result-object p0
    :try_end_4b
    .catchall {:try_start_22 .. :try_end_4b} :catchall_4c

    return-object p0

    :catchall_4c
    move-exception p0

    goto :goto_50

    :catchall_4e
    move-exception p0

    move-object v2, v1

    .line 175
    :goto_50
    invoke-static {v2}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->closeQuietly(Ljava/lang/Object;)V

    .line 176
    invoke-static {p0}, Lorg/vekendian/nexus/extensions/ExtensionLoader;->describe(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p0

    aput-object p0, p4, v0

    .line 177
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p1, "module load failed: "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    aget-object p1, p4, v0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "NexusMod"

    invoke-static {p1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    return-object v1
.end method

.method private static optimizedDir(Landroid/content/Context;)Ljava/lang/String;
    .registers 3

    :try_start_0
    const-string v0, "dex"

    const/4 v1, 0x0

    .line 188
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getDir(Ljava/lang/String;I)Ljava/io/File;

    move-result-object p0

    .line 190
    invoke-virtual {p0}, Ljava/io/File;->mkdirs()Z

    .line 191
    invoke-virtual {p0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object p0
    :try_end_e
    .catchall {:try_start_0 .. :try_end_e} :catchall_f

    return-object p0

    :catchall_f
    const/4 p0, 0x0

    return-object p0
.end method

.method private static readMeta(Ljava/lang/Class;Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;)V
    .registers 8
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/Class<",
            "*>;",
            "Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;",
            ")V"
        }
    .end annotation

    .line 205
    invoke-virtual {p0}, Ljava/lang/Class;->getAnnotations()[Ljava/lang/annotation/Annotation;

    move-result-object p0

    array-length v0, p0

    const/4 v1, 0x0

    const/4 v2, 0x0

    :goto_7
    if-ge v2, v0, :cond_96

    aget-object v3, p0, v2

    .line 206
    invoke-interface {v3}, Ljava/lang/annotation/Annotation;->annotationType()Ljava/lang/Class;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v4

    const-string v5, "org.vekendian.nexus.api.ExtensionManifest"

    invoke-virtual {v5, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-nez v4, :cond_1e

    add-int/lit8 v2, v2, 0x1

    goto :goto_7

    .line 210
    :cond_1e
    :try_start_1e
    invoke-interface {v3}, Ljava/lang/annotation/Annotation;->annotationType()Ljava/lang/Class;

    move-result-object p0

    const-string v0, "name"

    new-array v2, v1, [Ljava/lang/Class;

    invoke-virtual {p0, v0, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object p0

    new-array v0, v1, [Ljava/lang/Object;

    invoke-virtual {p0, v3, v0}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/String;

    iput-object p0, p1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->name:Ljava/lang/String;

    .line 211
    invoke-interface {v3}, Ljava/lang/annotation/Annotation;->annotationType()Ljava/lang/Class;

    move-result-object p0

    const-string v0, "description"

    new-array v2, v1, [Ljava/lang/Class;

    invoke-virtual {p0, v0, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object p0

    new-array v0, v1, [Ljava/lang/Object;

    invoke-virtual {p0, v3, v0}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/String;

    iput-object p0, p1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->description:Ljava/lang/String;

    .line 212
    invoke-interface {v3}, Ljava/lang/annotation/Annotation;->annotationType()Ljava/lang/Class;

    move-result-object p0

    const-string v0, "version"

    new-array v2, v1, [Ljava/lang/Class;

    invoke-virtual {p0, v0, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object p0

    new-array v0, v1, [Ljava/lang/Object;

    invoke-virtual {p0, v3, v0}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/Integer;

    invoke-virtual {p0}, Ljava/lang/Integer;->intValue()I

    move-result p0

    iput p0, p1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->version:I

    .line 213
    invoke-interface {v3}, Ljava/lang/annotation/Annotation;->annotationType()Ljava/lang/Class;

    move-result-object p0

    const-string v0, "autostart"

    new-array v2, v1, [Ljava/lang/Class;

    invoke-virtual {p0, v0, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object p0

    new-array v0, v1, [Ljava/lang/Object;

    invoke-virtual {p0, v3, v0}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/Boolean;

    invoke-virtual {p0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result p0

    iput-boolean p0, p1, Lorg/vekendian/nexus/extensions/ExtensionLoader$Meta;->autostart:Z
    :try_end_7e
    .catchall {:try_start_1e .. :try_end_7e} :catchall_7f

    goto :goto_96

    :catchall_7f
    move-exception p0

    .line 215
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "annotation read failed: "

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "NexusMod"

    invoke-static {p1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    :cond_96
    :goto_96
    return-void
.end method
