.class public interface abstract annotation Lorg/vekendian/nexus/api/ModuleManifest;
.super Ljava/lang/Object;
.source "ModuleManifest.java"

# interfaces
.implements Ljava/lang/annotation/Annotation;


# annotations
.annotation system Ldalvik/annotation/AnnotationDefault;
    value = .subannotation Lorg/vekendian/nexus/api/ModuleManifest;
        autostart = true
        dependsOn = {}
        description = ""
        entry = ""
        name = ""
        type = .enum Lorg/vekendian/nexus/api/ModuleType;->LUA:Lorg/vekendian/nexus/api/ModuleType;
        version = 0x1
    .end subannotation
.end annotation

.annotation runtime Ljava/lang/annotation/Retention;
    value = .enum Ljava/lang/annotation/RetentionPolicy;->RUNTIME:Ljava/lang/annotation/RetentionPolicy;
.end annotation

.annotation runtime Ljava/lang/annotation/Target;
    value = {
        .enum Ljava/lang/annotation/ElementType;->TYPE:Ljava/lang/annotation/ElementType;
    }
.end annotation


# virtual methods
.method public abstract autostart()Z
.end method

.method public abstract dependsOn()[Ljava/lang/String;
.end method

.method public abstract description()Ljava/lang/String;
.end method

.method public abstract entry()Ljava/lang/String;
.end method

.method public abstract name()Ljava/lang/String;
.end method

.method public abstract type()Lorg/vekendian/nexus/api/ModuleType;
.end method

.method public abstract version()I
.end method
