.class public final Lorg/vekendian/nexus/lua/NexusLua$Perm;
.super Ljava/lang/Object;
.source "NexusLua.java"


# The permission gate for every nexus.* call that needs a grant.
#
# The policy itself (what is granted, how keys are matched, why a stored denial
# cannot exist) lives in Java: org.vekendian.nexus.modules.PermRules, reached
# through LuaBridge.policy/remember. This class is the blocking half: build an
# Ask, post it to the main thread, park the script thread until the dialog
# closes or the timeout fires, then let the Ask report what happened.
#
# countDown happens in both onClick and onDismiss, so the latch never depends
# on which button listener ran: onClick sets the verdict, onDismiss releases
# the thread. A dialog dismissed from outside (back button, Activity teardown)
# therefore means decline, not deadlock.
#
# check() never throws: the Fn invoke() wrapper turns a false into
# "permission denied" and a script can carry on.
#
# Registers in check(): v0 latch/policy result, v1/v2 wide timeout, v3 unit,
# v4 ask, v5 allowed, v6 remember. .locals 7.


.method public static check(Ljava/lang/String;Ljava/lang/String;)Z
    .locals 7

    invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaBridge;->policy(Ljava/lang/String;Ljava/lang/String;)I

    move-result v0

    const/4 v1, 0x1

    if-eq v0, v1, :granted

    new-instance v0, Ljava/util/concurrent/CountDownLatch;

    invoke-direct {v0, v1}, Ljava/util/concurrent/CountDownLatch;-><init>(I)V

    new-instance v4, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;

    invoke-direct {v4, p0, p1, v0}, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/concurrent/CountDownLatch;)V

    invoke-static {v4}, Landroid/ext/n2;->i(Ljava/lang/Runnable;)V

    :try_start
    const-wide/32 v1, 0x927c0

    sget-object v3, Ljava/util/concurrent/TimeUnit;->MILLISECONDS:Ljava/util/concurrent/TimeUnit;

    invoke-virtual {v0, v1, v2, v3}, Ljava/util/concurrent/CountDownLatch;->await(JLjava/util/concurrent/TimeUnit;)Z
    :try_end
    .catch Ljava/lang/InterruptedException; {:try_start .. :try_end} :interrupted

    invoke-virtual {v4}, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->allowed()Z

    move-result v5

    if-eqz v5, :denied

    invoke-virtual {v4}, Lorg/vekendian/nexus/lua/NexusLua$Perm$Ask;->remember()Z

    move-result v6

    if-eqz v6, :granted

    invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaBridge;->remember(Ljava/lang/String;Ljava/lang/String;)V

    :granted
    const/4 v0, 0x1

    return v0

    :denied
    const/4 v0, 0x0

    return v0

    :interrupted
    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Thread;->interrupt()V

    const/4 v0, 0x0

    return v0
.end method
