.class public Lluaj/lib/jse/JseOsLib;
.super Lluaj/lib/OsLib;


# static fields
.field public static final EXEC_ERROR:I = -0x3

.field public static final EXEC_INTERRUPTED:I = -0x2

.field public static final EXEC_IOEXCEPTION:I = 0x1

.field private static cnt:J


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/OsLib;-><init>()V

    return-void
.end method


# virtual methods
.method protected T()Ljava/lang/String;
    .locals 5

    :try_start_0
    const-string v0, ".gg."

    const-string v1, ".tmp"

    invoke-static {v0, v1}, Ljava/io/File;->createTempFile(Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    return-object v0

    :catch_0
    const-class v0, Lluaj/lib/jse/JseOsLib;

    monitor-enter v0

    :try_start_3
    sget-wide v1, Lluaj/lib/jse/JseOsLib;->cnt:J

    const-wide/16 v3, 0x1

    add-long/2addr v3, v1

    sput-wide v3, Lluaj/lib/jse/JseOsLib;->cnt:J

    monitor-exit v0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, ".gg."

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    const-string v1, ".tmp"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-static {}, Landroid/ext/Tools;->b0()Ljava/io/File;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    :catchall_1
    move-exception v1

    :try_start_4
    monitor-exit v0
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1

    throw v1
.end method

.method protected a(Ljava/lang/String;)V
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    new-instance v0, Ljava/io/File;

    invoke-direct {v0, p1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result p1

    if-eqz p1, :cond_1

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result p1

    if-eqz p1, :cond_0

    return-void

    :cond_0
    new-instance p1, Ljava/io/IOException;

    const-string v0, "Failed to delete"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_1
    new-instance p1, Ljava/io/IOException;

    const-string v0, "No such file or directory"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method protected a(Ljava/lang/String;Ljava/lang/String;)V
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    new-instance v0, Ljava/io/File;

    invoke-direct {v0, p1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result p1

    if-eqz p1, :cond_1

    new-instance p1, Ljava/io/File;

    invoke-direct {p1, p2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, p1}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result p1

    if-eqz p1, :cond_0

    return-void

    :cond_0
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Failed to rename"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_1
    new-instance p1, Ljava/io/IOException;

    const-string p2, "No such file or directory"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method protected c(Ljava/lang/String;)Lluaj/Varargs;
    .locals 4

    :try_start_0
    new-instance v0, Lluaj/lib/jse/JseProcess;

    const/4 v1, 0x0

    iget-object v2, p0, Lluaj/lib/jse/JseOsLib;->T:Lluaj/Globals;

    iget-object v2, v2, Lluaj/Globals;->c0:Ljava/io/PrintStream;

    iget-object v3, p0, Lluaj/lib/jse/JseOsLib;->T:Lluaj/Globals;

    iget-object v3, v3, Lluaj/Globals;->d0:Ljava/io/PrintStream;

    invoke-direct {v0, p1, v1, v2, v3}, Lluaj/lib/jse/JseProcess;-><init>(Ljava/lang/String;Ljava/io/InputStream;Ljava/io/OutputStream;Ljava/io/OutputStream;)V

    invoke-virtual {v0}, Lluaj/lib/jse/JseProcess;->waitFor()I

    move-result p1
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/lang/InterruptedException; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    const/4 p1, -0x3

    goto :goto_0

    :catch_0
    const/4 p1, -0x2

    goto :goto_0

    :catch_1
    const/4 p1, 0x1

    :goto_0
    if-nez p1, :cond_0
    # nexus: pivot init (LuaBoolean TRUE via JseOsLib.v) was dropped by the port;
    # p1 holds the int exit code here and must be replaced before M2 (LuaValue arg)
    sget-object p1, Lluaj/LuaValue;->d:Lluaj/LuaBoolean;

    const-string v0, "exit"

    invoke-static {v0}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    sget-object v1, Lluaj/LuaValue;->g:Lluaj/LuaNumber;

    invoke-static {p1, v0, v1}, Lluaj/LuaValue;->M2(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object p1

    return-object p1

    :cond_0
    # nexus: pivot init (LuaValue NIL via JseOsLib.u) was dropped by the port;
    # v0 holds the JseProcess instance here and must be replaced before M2
    sget-object v0, Lluaj/LuaValue;->c:Lluaj/LuaValue;

    const-string v1, "signal"

    invoke-static {v1}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v1

    int-to-long v2, p1

    invoke-static {v2, v3}, Lluaj/LuaValue;->I2(J)Lluaj/LuaLong;

    move-result-object p1

    invoke-static {v0, v1, p1}, Lluaj/LuaValue;->M2(Lluaj/LuaValue;Lluaj/LuaValue;Lluaj/Varargs;)Lluaj/Varargs;

    move-result-object p1

    return-object p1
.end method

.method protected d(Ljava/lang/String;)Ljava/lang/String;
    .locals 1

    invoke-static {p1}, Ljava/lang/System;->getenv(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    invoke-static {p1}, Ljava/lang/System;->getProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :goto_0
    return-object v0
.end method
