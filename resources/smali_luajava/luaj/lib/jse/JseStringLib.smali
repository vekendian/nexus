.class public Lluaj/lib/jse/JseStringLib;
.super Lluaj/lib/StringLib;


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Lluaj/lib/StringLib;-><init>()V

    return-void
.end method


# virtual methods
.method protected format(Ljava/lang/String;D)Ljava/lang/String;
    .locals 3

    const/4 v0, 0x1

    :try_start_0
    new-array v0, v0, [Ljava/lang/Object;

    const/4 v1, 0x0

    invoke-static {p2, p3}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v2

    aput-object v2, v0, v1

    invoke-static {p1, v0}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception v0

    new-instance v1, Lluaj/d;

    invoke-direct {v1, v0}, Lluaj/d;-><init>(Ljava/lang/Throwable;)V

    throw v1

    :goto_0
    return-object p1
.end method
