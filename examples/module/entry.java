// A loadable Nexus module: the smallest thing the Dex Executor will run.
//
//   javac -cp build/module-api.jar -d build/example examples/module/entry.java
//   d8 --min-api 21 --output build/example-dex build/example/entry.class
//
// The Dex Executor imports the resulting classes.dex (rename it to hello.dex;
// the file itself is the raw dex, not an archive), finds the entry class by
// name -- `entry` or `nexus.entry` -- and calls run(NexusApi) on its own
// thread. Returning from run() means "finished"; an
// uncaught throwable means "error", and its message lands on the card.
//
// Two names are accepted and both are used in practice: this one, and
// `nexus.entry`. Nothing else is looked for: no manifest, no JSON, no base
// class. The @NexusModule annotation is required; it supplies the card text
// and a class without it is rejected at import time. The picked file must be
// a raw .dex -- APK/JAR/ZIP archives are not accepted.

import org.vekendian.nexus.api.NexusApi;
import org.vekendian.nexus.api.NexusModule;

@NexusModule(name = "Hello Nexus",
             description = "writes a line every second until stopped",
             version = 1,
             autostart = true)
public class entry {

    public void run(final NexusApi api) throws Exception {
        api.log("hello: modules dir is " + api.modulesDir());
        api.toast("Hello from a dex module");
        // A module runs to completion or until interrupted. stop() interrupts this
        // thread, which is how the power card stops everything: sleep() throws.
        for (int i = 0; i < 30; i++) {
            api.log("hello: tick " + i + " (Nexus " + api.appVersion() + ")");
            Thread.sleep(1000L);
        }
        api.log("hello: finished normally");
    }
}