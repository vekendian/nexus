.class public interface abstract Lorg/vekendian/nexus/api/ModuleApi;
.super Ljava/lang/Object;
.source "ModuleApi.java"


# virtual methods
.method public abstract activity()Landroid/app/Activity;
.end method

.method public abstract appVersion()Ljava/lang/String;
.end method

.method public abstract context()Landroid/content/Context;
.end method

.method public abstract getModuleClassLoader(Ljava/lang/String;)Ljava/lang/ClassLoader;
.end method

.method public abstract loadModule(Ljava/lang/String;)Ljava/lang/Object;
.end method

.method public abstract log(Ljava/lang/String;)V
.end method

.method public abstract modulesChanged()V
.end method

.method public abstract modulesDir()Ljava/lang/String;
.end method

.method public abstract toast(Ljava/lang/String;)V
.end method
