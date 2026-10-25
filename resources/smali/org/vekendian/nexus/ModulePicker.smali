.class public Lorg/vekendian/nexus/ModulePicker;
.super Landroid/app/Activity;
.source "ModulePicker.java"

# A result proxy for the extension picker.
#
# GameGuardian's activities are both launchMode="singleInstance". An activity
# in that mode always runs alone in its own task, and a launched activity joins
# a separate task -- so startActivityForResult() from one can never deliver a
# result back:
#
#   "Launching the picker from an Activity with launchMode: singleInstance will
#    always return RESULT_CANCELED. ... new activities are created in a separate
#    Task. As activities cannot communicate between tasks, the picker cannot
#    send back its eventual result to the calling activity."
#
# The picker opened fine and simply never came back, which is exactly the
# "picker opens, I pick, nothing happens" symptom.
#
# This class exists only to be a standard-launch-mode activity inside the host's
# task, call startActivityForResult() on ITSELF, park the chosen Uri in the
# extension system, and finish. The host drains it on the next onPostResume.
#
# Theme is translucent rather than NoDisplay: NoDisplay forbids the activity
# surviving onResume, and we have to stay alive to receive the result.

.method public constructor <init>()V
    .registers 1

    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .registers 6

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.OPEN_DOCUMENT"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v1, "*/*"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    const-string v1, "android.intent.category.OPENABLE"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;

    # Raw dex only. DexClassLoader can also read an archive's classes.dex, but
    # the executor deliberately rejects APK/JAR/ZIP so every import is one file
    # with one entry class. DocumentsUI narrows to this list for EXTRA_MIME_TYPES.
    const/4 v1, 0x2

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v3, "application/octet-stream"

    aput-object v3, v1, v2

    const/4 v2, 0x1

    const-string v3, "application/vnd.android.dex-archive"

    aput-object v3, v1, v2

    const-string v2, "android.intent.extra.MIME_TYPES"

    invoke-virtual {v0, v2, v1}, Landroid/content/Intent;->putExtra(Ljava/lang/String;[Ljava/lang/String;)Landroid/content/Intent;

    const v1, 0x4e58

    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent;I)V

    return-void
.end method

.method protected onActivityResult(IILandroid/content/Intent;)V
    # this + two ints + Intent = 4 parameter registers. .registers 4 would leave
    # zero locals, so v0 aliases `this`; overwriting it with an int and then
    # calling invoke-super on it fails verification with "tried to get class
    # from non-reference register v0 (type=Conflict)".
    # .registers 10 => p0=v9 p1=v8 p2=v7 p3=v6, locals v0..v5.
    .registers 10

    const-string v0, "NexusPick"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "onActivityResult req="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " res="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " data="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v0, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    const v3, 0x4e58

    if-ne p1, v3, :mp_finish

    if-eqz p2, :mp_finish

    if-eqz p3, :mp_finish

    invoke-virtual {p3}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object v0

    # ACTION_OPEN_DOCUMENT normally supplies data, but a malformed result must
    # not turn into a NullPointerException before the picker finishes.
    if-eqz v0, :mp_finish

    # Hand the document to the extension system. It used to be parked in a static on
    # android/ext/r; that field is gone -- NexusHost owns it now, so an extension
    # import cannot be lost to a field the host class no longer declares.
    invoke-static {p0, v0}, Lorg/vekendian/nexus/extensions/NexusHost;->parkFromActivity(Landroid/app/Activity;Landroid/net/Uri;)V

    invoke-virtual {v0}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v3

    const-string v1, "NexusPick"

    const-string v2, "parked "

    invoke-virtual {v2, v3}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-static {v1, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    :mp_finish
    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;->onActivityResult(IILandroid/content/Intent;)V

    invoke-virtual {p0}, Landroid/app/Activity;->finish()V

    return-void
.end method
