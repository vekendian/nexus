.class public Lluaj/a/t;
.super Lluaj/a/a;
.source "src"

# interfaces
.implements Lluaj/Pb;
.implements Lluaj/Pc;


# static fields
.field public static final b:Lluaj/a/t;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .prologue
    .line 78
    new-instance v0, Lluaj/a/t;

    invoke-direct {v0}, Lluaj/a/t;-><init>()V

    sput-object v0, Lluaj/a/t;->b:Lluaj/a/t;

    return-void
.end method

.method protected constructor <init>()V
    .locals 0

    .prologue
    .line 90
    invoke-direct {p0}, Lluaj/a/a;-><init>()V

    return-void
.end method

.method public static a(Lluaj/Globals;)V
    .locals 1

    .prologue
    .line 86
    sget-object v0, Lluaj/a/t;->b:Lluaj/a/t;

    iput-object v0, p0, Lluaj/Globals;->m:Lluaj/Pb;

    .line 87
    sget-object v0, Lluaj/a/t;->b:Lluaj/a/t;

    iput-object v0, p0, Lluaj/Globals;->l:Lluaj/Pc;

    .line 88
    return-void
.end method


# virtual methods
.method public a(Lluaj/al;Ljava/lang/String;Lluaj/LuaValue;)Lluaj/LuaFunction;
    .locals 2

    .prologue
    .line 103
    invoke-static {p1}, Lluaj/Hlp;->proto(Lluaj/al;)Lluaj/h;

    move-result-object p1

    new-instance v0, Lluaj/LuaClosure;

    const/4 v1, 0x1

    invoke-direct {v0, p1, p3, v1}, Lluaj/LuaClosure;-><init>(Lluaj/h;Lluaj/LuaValue;Z)V

    return-object v0
.end method

.method public a(Ljava/io/InputStream;Ljava/lang/String;)Lluaj/al;
    .locals 1

    .prologue
    .line 99
    new-instance v0, Lluaj/a/u;

    invoke-direct {v0}, Lluaj/a/u;-><init>()V

    invoke-virtual {v0, p1, p2}, Lluaj/a/u;->a(Ljava/io/InputStream;Ljava/lang/String;)Lluaj/al;

    move-result-object v0

    return-object v0
.end method
