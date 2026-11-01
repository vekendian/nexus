.class public final Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;
.super Ljava/lang/Object;
.source "NexusLua.java"

.implements Landroid/content/DialogInterface$OnClickListener;

.implements Landroid/content/DialogInterface$OnDismissListener;

.implements Ljava/lang/Runnable;


# The "Allow <script> to call <op>?" dialog and the script thread's answer.
#
# One instance per prompt. The script thread builds it, posts it (Runnable) to
# the main thread, and blocks on the latch; the main thread shows the dialog and
# reports the click back through decision. It must never hold the GG global
# lock or a dialog of its own while showing this one -- the prompt is posted
# with the same helper GG uses for its own script dialogs.
#
# Buttons: Allow once (positive) and Always allow (neutral) store the same
# decision, differing only in `remember`; Deny (negative) is just the lack of a
# decision. onDismiss counts down no matter which path closed the dialog, so a
# back-button dismissal reads as decline. Nothing is persisted here: Perm
# decides whether "Always allow" is remembered, one step later, so a crash or a
# race cannot leave a half-written grant.
#
# decision: 0 = not answered yet (decline), 1 = allow, 2 = deny. volatile
# because it is written on the main thread and read on the script thread, and
# the latch only orders the countDown that happens after the write.


.field private volatile decision:B

.field private final latch:Ljava/util/concurrent/CountDownLatch;

.field private final op:Ljava/lang/String;

.field private volatile remember:Z

.field private final script:Ljava/lang/String;


.method public constructor <init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/concurrent/CountDownLatch;)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->script:Ljava/lang/String;

    iput-object p2, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->op:Ljava/lang/String;

    iput-object p3, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->latch:Ljava/util/concurrent/CountDownLatch;

    return-void
.end method


.method public allowed()Z
    .locals 2

    iget-byte v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->decision:B

    const/4 v1, 0x1

    if-eq v0, v1, :yes

    const/4 v0, 0x0

    return v0

    :yes
    const/4 v0, 0x1

    return v0
.end method


.method public remember()Z
    .locals 1

    iget-boolean v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->remember:Z

    return v0
.end method


# Runs on the main thread. The strings are pinned resources (so they can be
# translated and stay in sync with the SETTINGS screen), the title is GG's
# custom-title view, and f.k/f.m are the same show-with-dismiss-dispatch
# helpers GG uses for script prompts.
#
# .locals 4 -> v0 builder/dialog, v1 id/string/view, v2 script, v3 op.


.method public run()V
    .locals 4

    invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;

    move-result-object v0

    if-eqz v0, :nexus_dialog_done

    const v1, @@ID:nexus_str_perm_title@@

    invoke-static {v1}, Landroid/ext/b2;->f(I)Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Landroid/ext/Tools;->h0(Ljava/lang/String;)Landroid/view/View;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setCustomTitle(Landroid/view/View;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const v1, @@ID:nexus_str_perm_msg@@

    iget-object v2, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->script:Ljava/lang/String;

    iget-object v3, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->op:Ljava/lang/String;

    invoke-static {v1, v2, v3}, Lorg/vekendian/nexus/modules/LuaBridge;->permMessage(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const v1, @@ID:nexus_str_perm_allow_once@@

    invoke-static {v1}, Landroid/ext/b2;->f(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1, p0}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const v1, @@ID:nexus_str_perm_always@@

    invoke-static {v1}, Landroid/ext/b2;->f(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1, p0}, Landroid/app/AlertDialog$Builder;->setNeutralButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const v1, @@ID:nexus_str_perm_deny@@

    invoke-static {v1}, Landroid/ext/b2;->f(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1, p0}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->create()Landroid/app/AlertDialog;

    move-result-object v0

    invoke-static {v0, p0}, Landroid/ext/f;->k(Landroid/app/AlertDialog;Landroid/content/DialogInterface$OnDismissListener;)V

    invoke-static {v0}, Landroid/ext/f;->m(Landroid/app/AlertDialog;)Landroid/app/AlertDialog;

    :nexus_dialog_done
    return-void
.end method


# Main thread. which is BUTTON_POSITIVE (-1), BUTTON_NEUTRAL (-3) or
# BUTTON_NEGATIVE (-2); the verdict is written before countDown, so the script
# thread always sees it (latch establishes the happens-before).
#
# .locals 3 -> v0 ALLOW, v1 button/decision scratch.


.method public onClick(Landroid/content/DialogInterface;I)V
    .locals 3

    const/4 v0, 0x1

    const/4 v1, -0x1

    if-eq p2, v1, :neutral

    iput-byte v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->decision:B

    const/4 v1, 0x0

    iput-boolean v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->remember:Z

    goto :count

    :neutral
    const/4 v1, -0x3

    if-eq p2, v1, :negative

    iput-byte v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->decision:B

    iput-boolean v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->remember:Z

    goto :count

    :negative
    const/4 v1, 0x2

    iput-byte v1, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->decision:B

    :count
    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->latch:Ljava/util/concurrent/CountDownLatch;

    invoke-virtual {v0}, Ljava/util/concurrent/CountDownLatch;->countDown()V

    return-void
.end method


.method public onDismiss(Landroid/content/DialogInterface;)V
    .locals 1

    iget-object v0, p0, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->latch:Ljava/util/concurrent/CountDownLatch;

    invoke-virtual {v0}, Ljava/util/concurrent/CountDownLatch;->countDown()V

    return-void
.end method
