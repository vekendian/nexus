.class public interface abstract Lorg/vekendian/nexus/api/NexusExecutor;
.super Ljava/lang/Object;
.source "NexusExecutor.java"


# virtual methods
.method public abstract add(Landroid/content/Context;Landroid/net/Uri;)Ljava/lang/String;
.end method

.method public abstract extensions()Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Ljava/util/List<",
            "Lorg/vekendian/nexus/api/ExtensionInfo;",
            ">;"
        }
    .end annotation
.end method

.method public abstract failure()Ljava/lang/String;
.end method

.method public abstract jarInvoke(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;
.end method

.method public abstract jarSpec(Ljava/lang/String;)[Ljava/lang/String;
.end method

.method public abstract loadExtension(Ljava/lang/String;)Ljava/lang/Object;
.end method

.method public abstract loadLibrary(Ljava/lang/String;)Ljava/lang/ClassLoader;
.end method

.method public abstract luaSource(Ljava/lang/String;)[Ljava/lang/String;
.end method

.method public abstract remove(Ljava/lang/String;)Z
.end method

.method public abstract run(Ljava/lang/String;)Z
.end method

.method public abstract runAll()V
.end method

.method public abstract stop(Ljava/lang/String;)V
.end method

.method public abstract stopAll()V
.end method
