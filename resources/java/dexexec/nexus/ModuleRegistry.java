package nexus;

import android.content.Context;
import android.net.Uri;
import android.util.Log;

import org.vekendian.nexus.api.ModuleApi;
import org.vekendian.nexus.api.ModuleInfo;
import org.vekendian.nexus.api.ModuleManifest;
import org.vekendian.nexus.api.ModuleType;
import org.vekendian.nexus.api.NexusExecutor;

import java.io.File;
import java.io.FileInputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Module Registry: the module system's built-in module, and the reason the
 * module system exists.
 *
 * <p>Nexus could only execute Lua. GameGuardian's executor is
 * {@code android.ext.Script} -- a LuaJ state per script, started with
 * {@code Script.R3()}, stopped with {@code Script.x3(1)}, run on a
 * {@code Script$ScriptThread}, with results handed back through
 * {@code MainService}. This class is the same shape for .lua/.jar: a picked document
 * is imported into clean app storage, loaded with a DexClassLoader (for JAR) or
 * loadstring (for Lua), and its entry runs on its own thread until it returns or is
 * interrupted.
 *
 * <p>Nothing GameGuardian owns is touched. The registry is a plain module as far
 * as Nexus is concerned: it is loaded from a .dex asset by the same code path
 * that loads anything else, and the MODULES tab only ever talks to it through
 * {@link NexusExecutor}.
 *
 * <p>Every module is isolated in its own classloader and every failure lands on
 * that module's own card, so a module that throws cannot take the registry -- let
 * alone Nexus -- with it.
 *
 * <p><b>JAR modules:</b> JAR modules export classes via a shared
 * classloader. They have no card, no run(), and no auto-start. Other modules
 * declare {@code dependsOn: ["library-id"]} to access them via
 * {@link ModuleApi#getModuleClassLoader(String)}.
 */
@ModuleManifest(name = "Module Registry",
             description = "Run .lua modules; load .jar/.dex libraries",
             version = 1)
public final class ModuleRegistry implements NexusExecutor {

    private static final String TAG = "NexusMod";
    private static final String PREFS = "nexus_modules";

    /** Guards every field below. Held across classloader work, never across an
     *  module's run(): a module that runs for minutes must not hold this. */
    private final Object lock = new Object();

    private final List<ModuleRecord> records = new ArrayList<ModuleRecord>();

    private volatile ModuleApi api;
    private ModuleStore store;
    private volatile boolean ready;

    /** True once restore() has published its snapshot. Written under lock. */
    private boolean restored;

    /** How long a caller waits for the asynchronous restore. */
    private static final long RESTORE_WAIT_MS = 5000L;

    // ------------------------------------------------------------ lifecycle ---

    /** Entry-class lifecycle, called by the module system after instantiation. */
    public void onLoad(ModuleApi api) {
        final Context context = api == null ? null : api.context();
        synchronized (lock) {
            this.api = api;
            if (ready) {
                return;
            }
            ready = true;
            if (context != null) {
                // Created here, before an import can race the async restore, so
                // there is never more than one store writing the same prefs.
                store = new ModuleStore(context, api);
            }
        }
        // Registering paths means creating a classloader per module, which is
        // disk I/O: it cannot happen on the thread that called onLoad (the host's
        // onPostResume) without dropping frames.
        Thread t = new Thread(new Runnable() {
            public void run() {
                restore();
            }
        }, "NexusModules:restore");
        t.start();
    }

    /** Entry-class lifecycle: nothing to undo, modules are stopped by stopAll. */
    public void onUnload() {
        stopAll();
    }

    /** Rebuilds the module list from prefs, off the caller's thread. */
    private void restore() {
        final Context context = api == null ? null : api.context();
        final ModuleStore s = store;
        if (context == null || s == null) {
            finishRestore();
            return;
        }
        try {
            List<ModuleStore.Entry> entries = s.entries();
            List<ModuleRecord> fresh = new ArrayList<ModuleRecord>();
            for (int i = 0; i < entries.size(); i++) {
                ModuleStore.Entry entry = entries.get(i);
                ModuleRecord rec = new ModuleRecord(entry.path);
                rec.type = entry.type;
                rec.dependsOn = entry.dependsOn;
                String err = prepareModule(context, rec, getSharedLibraryLoaderLocked());
                if (err == null) {
                    fresh.add(rec);
                } else {
                    // Kept rather than dropped: a module whose file is broken is
                    // something the user needs to see, with the reason on it.
                    rec.state = ModuleInfo.STATE_ERROR;
                    rec.message = err;
                    fresh.add(rec);
                }
            }
            synchronized (lock) {
                // An import can land while this thread is preparing classloaders.
                // It is already in prefs and must not be erased by the snapshot.
                // A running record always wins over the fresh snapshot, otherwise
                // restore would orphan a module thread with no card.
                for (int i = 0; i < records.size(); i++) {
                    ModuleRecord extra = records.get(i);
                    ModuleRecord duplicate = findRecord(fresh, extra.path);
                    if (duplicate == null) {
                        fresh.add(extra);
                    } else {
                        int at = fresh.indexOf(duplicate);
                        fresh.set(at, extra);
                        releaseRecord(duplicate);
                    }
                }
                records.clear();
                records.addAll(fresh);
            }
            // Published before runAll(): a module started there calls back
            // into modules()/import() immediately and must not wait on us.
            finishRestore();
            runAll();
        } catch (Throwable t) {
            Log.e(TAG, "restore failed: " + describe(t));
        } finally {
            finishRestore();
            changed();
        }
    }

    /** Wakes every caller waiting for the asynchronous restore. */
    private void finishRestore() {
        synchronized (lock) {
            restored = true;
            lock.notifyAll();
        }
    }

    /**
     * Waits for the restore() snapshot, bounded.
     *
     * <p>A script can run in the same resume that starts restore(). Without
     * this wait it sees no modules, installs a second copy of one already
     * present, and then imports the id it asked for -- which is the copy it
     * did not get.
     *
     * <p>Callers must not hold {@link #lock}: restore() takes it to publish.
     * A timeout is not a failure -- an empty answer is still an answer, and a
     * script must not hang because a classloader is slow.
     */
    private void awaitRestore() {
        if (!ready) {
            return;
        }
        synchronized (lock) {
            long deadline = System.currentTimeMillis() + RESTORE_WAIT_MS;
            while (!restored) {
                long left = deadline - System.currentTimeMillis();
                if (left <= 0) {
                    Log.e(TAG, "restore still running after " + RESTORE_WAIT_MS + "ms");
                    return;
                }
                try {
                    lock.wait(left);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    // ------------------------------------------------------------- executor ---

    @Override
    public List<ModuleInfo> modules() {
        awaitRestore();
        List<ModuleInfo> out = new ArrayList<ModuleInfo>();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                // Every record gets a card: JARs are libraries, so theirs is
                // metadata-only (the host hides Run/Stop), and the Lua list op
                // must be able to see an installed library too.
                out.add(records.get(i).info());
            }
        }
        return out;
    }

    @Override
    public String add(Context context, Uri uri) {
        if (uri == null || context == null) {
            return null;
        }
        if (api == null) {
            return null;
        }
        awaitRestore();
        if (store == null) {
            store = new ModuleStore(context, api);
        }
        // Installing a module that is already there is a no-op, not a second
        // copy. Without this, a script that cannot tell whether a module is
        // present ("install, then import") leaves Eclipse-2.dex behind and
        // then imports the id it asked for, which is the copy it did not get.
        String wanted = idOf(Name.storedName(store.displayNameOf(uri)));
        String present = pathOfId(wanted);
        if (present != null) {
            store.release(uri);
            Log.e(TAG, "import skipped, already installed: " + present);
            return present;
        }
        File imported = store.importUri(uri);
        if (imported == null) {
            Log.e(TAG, "import rejected: " + uri);
            return null;
        }
        ModuleRecord rec = new ModuleRecord(imported.getAbsolutePath());
        // Detect type by file extension
        String name = imported.getName().toLowerCase();
        if (name.endsWith(".jar")) {
            rec.type = ModuleType.JAR;
        } else if (name.endsWith(".lua")) {
            rec.type = ModuleType.LUA;
        } else if (name.endsWith(".dex")) {
            rec.type = ModuleType.DEX;
        } else {
            // Unknown module type - reject
            store.release(uri);
            Log.e(TAG, "import rejected: unknown module type for " + imported.getName());
            return null;
        }
        // Prepare with current shared library loader (dependencies already loaded)
        String err = prepareModule(context, rec, getSharedLibraryLoaderLocked());
        if (err != null) {
            // A rejected import must not leave a card, a file or a dangling URI
            // grant behind. The error is logged and the caller gets null.
            releaseRecord(rec);
            store.delete(imported);
            store.release(uri);
            Log.e(TAG, "import rejected: " + rec.path + " (" + err + ")");
            return null;
        }
        // If this is a JAR/DEX, we need to make its shared loader available to dependents
        if ((rec.type == ModuleType.JAR || rec.type == ModuleType.DEX)
                && rec.sharedLoader != null) {
            Log.e(TAG, "library module loaded: " + rec.path + " -> shared loader ready");
        }
        // The copy is the only thing Nexus uses; the document grant is no
        // longer needed once the file is in app-private storage.
        ModuleRecord raced;
        synchronized (lock) {
            // Two installs of the same document can overlap (the picker and a
            // script, or two scripts). The first record wins and the second
            // copy is dropped, so the id never gains a "-2" suffix.
            raced = recordOfIdLocked(wanted);
            if (raced == null) {
                records.add(rec);
            }
        }
        if (raced != null) {
            releaseRecord(rec);
            store.delete(imported);
            Log.e(TAG, "import raced, already installed: " + raced.path);
            return raced.path;
        }
        store.addEntry(rec.path, rec.type, rec.dependsOn);
        Log.e(TAG, "imported " + rec.path + " (type=" + rec.type + ")");
        // A freshly added autostart module starts now rather than waiting for the
        // next resume, which is what a user who just tapped "+" expects.
        if (rec.autostart && rec.type != ModuleType.JAR && rec.type != ModuleType.DEX) {
            run(rec.path);
        }
        // Re-check waiting modules that might depend on this new JAR
        recheckDependents();
        return rec.path;
    }

    @Override
    public boolean remove(String id) {
        if (id == null) {
            return false;
        }
        awaitRestore();
        ModuleRecord target = null;
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                if (id.equals(records.get(i).path)) {
                    target = records.remove(i);
                    break;
                }
            }
            if (target == null) {
                return false;
            }
            if (store != null) {
                store.removePath(target.path);
            }
        }
        releaseRecord(target);
        if (store != null) {
            store.delete(new File(target.path));
        }
        Log.e(TAG, "removed " + target.path);
        // If we removed a JAR, dependents may now be broken
        recheckDependents();
        return true;
    }

    @Override
    public boolean run(String id) {
        ModuleRecord rec = find(id);
        if (rec == null || rec.running()) {
            return false;
        }
        // JAR/DEX modules cannot be run: they are libraries
        if (rec.type == ModuleType.JAR || rec.type == ModuleType.DEX) {
            return false;
        }
        startModule(this, rec, api);
        changed();
        Log.e(TAG, "started " + rec.path);
        return true;
    }

    @Override
    public void stop(String id) {
        ModuleRecord rec = find(id);
        if (rec != null) {
            stopModule(rec);
            changed();
        }
    }

    @Override
    public void runAll() {
        if (api == null) {
            return;
        }
        List<ModuleRecord> snapshot;
        synchronized (lock) {
            snapshot = new ArrayList<ModuleRecord>(records);
        }
        for (int i = 0; i < snapshot.size(); i++) {
            ModuleRecord rec = snapshot.get(i);
            // JAR/DEX modules don't run
            if (rec.type == ModuleType.JAR || rec.type == ModuleType.DEX) continue;
            // FINISHED and ERROR are terminal: a module that completed its work
            // is not re-run by every resume, and one that crashed stays visible
            // as an error instead of being restarted into the same crash.
            if (rec.autostart && !rec.running()
                    && rec.state != ModuleInfo.STATE_FINISHED
                    && rec.state != ModuleInfo.STATE_ERROR) {
                startModule(this, rec, api);
                Log.e(TAG, "autostart " + rec.path);
            }
        }
    }

    @Override
    public void stopAll() {
        List<ModuleRecord> snapshot;
        synchronized (lock) {
            snapshot = new ArrayList<ModuleRecord>(records);
        }
        for (int i = 0; i < snapshot.size(); i++) {
            stopModule(snapshot.get(i));
        }
        changed();
    }

    @Override
    public String failure() {
        return null;
    }

    @Override
    public ClassLoader loadLibrary(String moduleId) {
        awaitRestore();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                if ((rec.type == ModuleType.JAR || rec.type == ModuleType.DEX)
                        && rec.sharedLoader != null) {
                    String label = rec.label();
                    // Match by filename without .jar/.dex
                    if (label.endsWith(".jar")) {
                        label = label.substring(0, label.length() - 4);
                    } else if (label.endsWith(".dex")) {
                        label = label.substring(0, label.length() - 4);
                    }
                    if (label.equals(moduleId)) {
                        return rec.sharedLoader;
                    }
                }
            }
            return null;
        }
    }

    @Override
    public Object loadModule(String moduleId) {
        // Called from Lua via ModuleApi.loadModule(); matching is by the
        // filename without its .lua/.jar suffix.
        awaitRestore();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                String label = rec.label();
                // Match by filename without .lua/.jar
                if (label.endsWith(".lua")) {
                    label = label.substring(0, label.length() - 4);
                } else if (label.endsWith(".jar")) {
                    label = label.substring(0, label.length() - 4);
                } else if (label.endsWith(".dex")) {
                    label = label.substring(0, label.length() - 4);
                }
                if (label.equals(moduleId)) {
                    // A manifest-declared JAR hands over its entry instance,
                    // which LuaJava can reflect on; a library JAR has none.
                    if (rec.type == ModuleType.JAR || rec.type == ModuleType.DEX) {
                        return rec.instance;
                    }
                    // A .lua module's handle is its own path: Lua gets a
                    // string it can recognise, not a live chunk, because
                    // running the source is the supported surface.
                    return rec.path;
                }
            }
            return null;
        }
    }

    @Override
    public String[] jarSpec(String moduleId) {
        awaitRestore();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                if (rec.type != ModuleType.JAR && rec.type != ModuleType.DEX) {
                    continue;
                }
                String label = rec.label();
                if (label.endsWith(".jar")) {
                    label = label.substring(0, label.length() - 4);
                } else if (label.endsWith(".dex")) {
                    label = label.substring(0, label.length() - 4);
                }
                if (label.equals(moduleId)) {
                    return buildJarSpec(rec);
                }
            }
            return new String[0];
        }
    }

    @Override
    public String[] jarInvoke(String moduleId, String method, String packedArgs) {
        awaitRestore();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                if (rec.type != ModuleType.JAR && rec.type != ModuleType.DEX) {
                    continue;
                }
                String label = rec.label();
                if (label.endsWith(".jar")) {
                    label = label.substring(0, label.length() - 4);
                } else if (label.endsWith(".dex")) {
                    label = label.substring(0, label.length() - 4);
                }
                if (label.equals(moduleId)) {
                    return invokeJarMethod(rec, method, packedArgs);
                }
            }
            return new String[]{"e", "module not found or not a jar/dex"};
        }
    }

    @Override
    public String[] luaSource(String moduleId) {
        awaitRestore();
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                if (rec.type != ModuleType.LUA) {
                    continue;
                }
                String label = rec.label();
                if (label.endsWith(".lua")) {
                    label = label.substring(0, label.length() - 4);
                }
                if (label.equals(moduleId)) {
                    try {
                        String source = new String(java.nio.file.Files.readAllBytes(
                                java.nio.file.Paths.get(rec.path)), "UTF-8");
                        // The envelope the Lua Import builder loads: {"r", source}.
                        // A plain one-element array reads as a missing envelope and
                        // falls through to "nothing importable at <id>".
                        return new String[]{"r", source};
                    } catch (Throwable t) {
                        return new String[]{"e", "cannot read lua source: " + describe(t)};
                    }
                }
            }
            return new String[0];
        }
    }

    /** Builds export records for a JAR/DEX entry class. Caches in rec.exportedMethods. */
    private String[] buildJarSpec(ModuleRecord rec) {
        // Use cached spec if available
        if (rec.exportedMethods != null) {
            return rec.exportedMethods;
        }
        if (rec.entry == null) {
            return new String[0];
        }
        java.util.List<String> specs = new java.util.ArrayList<>();
        for (java.lang.reflect.Method m : rec.entry.getMethods()) {
            if (!m.isAnnotationPresent(org.vekendian.nexus.api.Export.class)) {
                continue;
            }
            // Skip Object methods and bridge methods
            if (m.getDeclaringClass() == Object.class || m.isBridge()) {
                continue;
            }
            // Build param spec
            Class<?>[] params = m.getParameterTypes();
            StringBuilder pspec = new StringBuilder();
            boolean hasVarargs = false;
            for (int i = 0; i < params.length; i++) {
                Class<?> p = params[i];
                char code;
                if (p == String.class) {
                    code = 'p';
                } else if (p == int.class || p == Integer.class || p == long.class || p == Long.class) {
                    code = 'i';
                } else if (p == double.class || p == Double.class || p == float.class || p == Float.class) {
                    code = 'n';
                } else if (p == boolean.class || p == Boolean.class) {
                    code = 'b';
                } else if (p == String[].class && i == params.length - 1) {
                    code = 'a'; // varargs
                    hasVarargs = true;
                } else {
                    // Unsupported type - skip this method
                    pspec = null;
                    break;
                }
                pspec.append(code);
            }
            if (pspec == null) {
                continue;
            }
            // Build return spec
            Class<?> ret = m.getReturnType();
            char rcode;
            if (ret == void.class) {
                rcode = 'v';
            } else if (ret == String.class) {
                rcode = 's';
            } else if (ret == int.class || ret == Integer.class || ret == long.class || ret == Long.class) {
                rcode = 'n';
            } else if (ret == double.class || ret == Double.class || ret == float.class || ret == Float.class) {
                rcode = 'n';
            } else if (ret == boolean.class || ret == Boolean.class) {
                rcode = 'b';
            } else {
                continue; // unsupported return type
            }
            // Get explicit name from annotation or use method name
            org.vekendian.nexus.api.Export ann = m.getAnnotation(org.vekendian.nexus.api.Export.class);
            String name = ann.value().isEmpty() ? m.getName() : ann.value();
            specs.add(name + "\t" + pspec.toString() + "\t" + rcode);
        }
        String[] arr = specs.toArray(new String[0]);
        rec.exportedMethods = arr;
        return arr;
    }

    /** Invokes a method on the entry instance with packed arguments. */
    private String[] invokeJarMethod(ModuleRecord rec, String methodName, String packedArgs) {
        if (rec.instance == null || rec.entry == null) {
            return new String[]{"e", "no entry instance"};
        }
        // Find the spec for this method
        String[] specs = buildJarSpec(rec);
        String pspec = null;
        char rcode = 'v';
        java.lang.reflect.Method target = null;
        for (String spec : specs) {
            String[] parts = spec.split("\t");
            if (parts.length == 3 && parts[0].equals(methodName)) {
                pspec = parts[1];
                rcode = parts[2].charAt(0);
                try {
                    // Find matching method by name and parameter types
                    Class<?>[] paramTypes = new Class<?>[pspec.length()];
                    for (int i = 0; i < pspec.length(); i++) {
                        char c = pspec.charAt(i);
                        if (c == 'p') paramTypes[i] = String.class;
                        else if (c == 'i') paramTypes[i] = int.class;
                        else if (c == 'n') paramTypes[i] = double.class;
                        else if (c == 'b') paramTypes[i] = boolean.class;
                        else if (c == 'a') paramTypes[i] = String[].class;
                    }
                    target = rec.entry.getMethod(methodName, paramTypes);
                } catch (NoSuchMethodException e) {
                    return new String[]{"e", "method signature mismatch"};
                }
                break;
            }
        }
        if (target == null || pspec == null) {
            return new String[]{"e", "method not exported: " + methodName};
        }
        // Parse packed args
        String[] args = unpackArgs(packedArgs);
        // Validate arity (account for varargs)
        int minArgs = pspec.length();
        if (pspec.indexOf('a') >= 0) minArgs--; // varargs is optional
        if (args.length < minArgs) {
            return new String[]{"e", "arity mismatch: expected at least " + minArgs + " args, got " + args.length};
        }
        // Coerce args
        Object[] coerced = new Object[pspec.length()];
        int argIdx = 0;
        for (int i = 0; i < pspec.length(); i++) {
            char c = pspec.charAt(i);
            if (c == 'a') {
                // varargs: collect remaining args
                String[] varargs = new String[args.length - argIdx];
                System.arraycopy(args, argIdx, varargs, 0, varargs.length);
                coerced[i] = varargs;
                break;
            } else if (argIdx >= args.length) {
                return new String[]{"e", "missing argument at position " + i};
            } else {
                String raw = args[argIdx++];
                try {
                    if (c == 'p') coerced[i] = raw;
                    else if (c == 'i') coerced[i] = Integer.parseInt(raw);
                    else if (c == 'n') coerced[i] = Double.parseDouble(raw);
                    else if (c == 'b') coerced[i] = Boolean.parseBoolean(raw);
                    else coerced[i] = raw;
                } catch (NumberFormatException e) {
                    return new String[]{"e", "argument " + i + " type mismatch: " + e.getMessage()};
                }
            }
        }
        // Invoke
        try {
            Object result = target.invoke(rec.instance, coerced);
            // Marshal result
            if (rcode == 'v') {
                return new String[]{"r", ""};
            } else if (rcode == 's') {
                return new String[]{"r", result == null ? "" : String.valueOf(result)};
            } else if (rcode == 'n') {
                if (result instanceof Number) {
                    return new String[]{"r", String.valueOf(((Number) result).doubleValue())};
                }
                return new String[]{"r", "0"};
            } else if (rcode == 'b') {
                return new String[]{"r", result == null ? "false" : String.valueOf(result)};
            }
            return new String[]{"r", result == null ? "" : String.valueOf(result)};
        } catch (java.lang.reflect.InvocationTargetException e) {
            Throwable cause = e.getCause();
            return new String[]{"e", cause != null ? cause.getMessage() : e.getMessage()};
        } catch (Throwable t) {
            return new String[]{"e", describe(t)};
        }
    }

    /** Unpacks tab-joined args with backslash escaping. */
    private String[] unpackArgs(String packed) {
        if (packed == null || packed.length() == 0) {
            return new String[0];
        }
        java.util.List<String> out = new java.util.ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean escape = false;
        for (int i = 0; i < packed.length(); i++) {
            char c = packed.charAt(i);
            if (escape) {
                if (c == 't') cur.append('\t');
                else if (c == 'n') cur.append('\n');
                else if (c == '\\') cur.append('\\');
                else cur.append(c);
                escape = false;
            } else if (c == '\\') {
                escape = true;
            } else if (c == '\t') {
                out.add(cur.toString());
                cur.setLength(0);
            } else {
                cur.append(c);
            }
        }
        out.add(cur.toString());
        return out.toArray(new String[0]);
    }

    // ---------------------------------------------------- module callbacks ---

    /** An module's run() returned: done, unless we asked it to stop. */
    void finished(ModuleRecord rec, boolean stopped) {
        synchronized (lock) {
            if (rec.thread != Thread.currentThread()) {
                return;                 // a newer run already owns this record
            }
            rec.thread = null;
            rec.state = stopped ? ModuleInfo.STATE_STOPPED : ModuleInfo.STATE_FINISHED;
            rec.message = null;
        }
        releaseIfReleased(rec);
        changed();
    }

    /** An module threw: keep the message on its card, never propagate. */
    void failed(ModuleRecord rec, Throwable t) {
        String why = describe(t);
        synchronized (lock) {
            if (rec.thread != Thread.currentThread()) {
                return;
            }
            rec.thread = null;
            rec.state = rec.stopRequested ? ModuleInfo.STATE_STOPPED
                                          : ModuleInfo.STATE_ERROR;
            rec.message = why;
        }
        releaseIfReleased(rec);
        changed();
        Log.e(TAG, "module error " + rec.path + ": " + why);
    }

    // --------------------------------------------------------------- helpers ---

    private ModuleRecord find(String id) {
        synchronized (lock) {
            for (int i = 0; i < records.size(); i++) {
                if (id.equals(records.get(i).path)) {
                    return records.get(i);
                }
            }
        }
        return null;
    }

    /** Ask the host to repaint after a change made off the UI thread. */
    private void changed() {
        ModuleApi a = api;
        if (a == null) {
            return;
        }
        try {
            a.modulesChanged();
        } catch (Throwable t) {
            Log.e(TAG, "modulesChanged failed: " + describe(t));
        }
    }

    /** A stored file's module id: its label without the type suffix. */
    private static String idOf(String label) {
        return ModuleRecord.stripSuffix(label);
    }

    /** The record whose module id is {@code id}, or null. Caller holds lock. */
    private ModuleRecord recordOfIdLocked(String id) {
        for (int i = 0; i < records.size(); i++) {
            if (id.equals(idOf(records.get(i).label()))) {
                return records.get(i);
            }
        }
        return null;
    }

    /** The path of the record whose module id is {@code id}, or null. */
    private String pathOfId(String id) {
        synchronized (lock) {
            ModuleRecord rec = recordOfIdLocked(id);
            return rec == null ? null : rec.path;
        }
    }

    private static ModuleRecord findRecord(List<ModuleRecord> list, String path) {
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).path.equals(path)) {
                return list.get(i);
            }
        }
        return null;
    }

    /** Returns the shared classloader for JAR or DEX modules, or null if none loaded. */
    private ClassLoader getSharedLibraryLoaderLocked() {
        synchronized (lock) {
            ClassLoader first = null;
            for (int i = 0; i < records.size(); i++) {
                ModuleRecord rec = records.get(i);
                if ((rec.type == ModuleType.JAR || rec.type == ModuleType.DEX)
                        && rec.sharedLoader != null && rec.sharedLoader != first) {
                    if (first == null) {
                        first = rec.sharedLoader;
                    }
                }
            }
            return first;
        }
    }

    /** Checks that {@code f} is a Dalvik-dex file (starts with the dex magic). */
    private static boolean isDex(File f) {
        if (f == null || !f.isFile() || f.length() < 4) {
            return false;
        }
        FileInputStream in = null;
        try {
            in = new FileInputStream(f);
            byte[] magic = new byte[4];
            int n = 0;
            while (n < magic.length) {
                int r = in.read(magic, n, magic.length - n);
                if (r <= 0) {
                    return false;
                }
                n += r;
            }
            // "dex\n" = 0x64 0x65 0x78 0x0a
            return magic[0] == 'd' && magic[1] == 'e' && magic[2] == 'x' && magic[3] == '\n';
        } catch (Throwable t) {
            return false;
        } finally {
            ModuleStore.closeQuietly(in);
        }
    }

    /** Prepares a module based on its type (LUA or JAR). */
    private String prepareModule(Context context, ModuleRecord rec, ClassLoader sharedLibraryLoader) {
        File f = new File(rec.path);
        if (!f.isFile()) {
            return fail(rec, "file is gone");
        }
        try {
            if (rec.type == ModuleType.JAR || rec.type == ModuleType.DEX) {
                // Validate JAR/DEX
                if (rec.type == ModuleType.JAR) {
                    if (!JarModuleLoader.isJar(f)) {
                        return fail(rec, "not a valid .jar file");
                    }
                } else if (!isDex(f)) {
                    return fail(rec, "not a valid .dex file");
                }
                return JarModuleLoader.prepare(context, rec, sharedLibraryLoader);
            } else {
                // Lua module - validate it's a Lua file
                if (!f.getName().toLowerCase().endsWith(".lua")) {
                    return fail(rec, "not a .lua file");
                }
                // For Lua, we don't need a classloader - it's loaded via loadstring
                // Just validate the file exists and is readable
                FileInputStream in = null;
                try {
                    in = new FileInputStream(f);
                    // Read first few bytes to verify it's text
                    byte[] buf = new byte[Math.min(1024, (int) f.length())];
                    in.read(buf);
                    // Check it's not a binary file
                    for (byte b : buf) {
                        if (b == 0) {
                            return fail(rec, "file appears to be binary, not Lua source");
                        }
                    }
                } catch (Throwable t) {
                    return fail(rec, "cannot read Lua file: " + t.getMessage());
                } finally {
                    if (in != null) {
                        try { in.close(); } catch (Throwable ignored) {}
                    }
                }
                // A card needs a title even though no manifest was read: the
                // module id it stands for, without the file's type suffix.
                if (rec.name == null || rec.name.length() == 0) {
                    rec.name = rec.id();
                }
                if (rec.description == null) {
                    rec.description = "";
                }
                return null;
            }
        } catch (Throwable t) {
            return fail(rec, describe(t));
        }
    }

    /** Drops a half-built loader so a rejected module does not leak it. */
    private String fail(ModuleRecord rec, String why) {
        if (rec.name == null || rec.name.length() == 0) {
            rec.name = rec.id();
        }
        releaseRecord(rec);
        return why;
    }

    /**
     * Runs one module on a fresh thread.
     *
     * <p>JAR modules are libraries and are never started. A .lua module
     * has no Java entry class to reflect on -- its source is handed to
     * GameGuardian's own LuaJ (loadstring) by {@link LuaModuleLoader}, which
     * also installs the {@code nexus.*} table so a module can call
     * {@code nexus.modules.*} like any script can.
     */
    static void startModule(final ModuleRegistry host, final ModuleRecord rec, final ModuleApi api) {
        // JAR/DEX modules have no run() - they should never be started
        if (rec.type == ModuleType.JAR || rec.type == ModuleType.DEX) {
            return;
        }
        LuaModuleLoader.start(host, rec);
    }

    /** Asks a running module to stop: flag first, then interrupt. */
    static void stopModule(ModuleRecord rec) {
        rec.stopRequested = true;
        Thread t = rec.thread;
        if (t != null && t.isAlive()) {
            t.interrupt();
        }
        if (rec.state == ModuleInfo.STATE_RUNNING) {
            rec.state = ModuleInfo.STATE_STOPPED;
        }
    }

    /**
     * Releases a record immediately, or marks it for release once its running
     * thread has unwound. Closing a classloader under a live module would make
     * its next class resolution fail with a confusing error.
     */
    static void releaseRecord(ModuleRecord rec) {
        rec.released = true;
        stopModule(rec);
        if (!rec.running()) {
            closeLoader(rec);
        }
    }

    /** Called by the executor after a run has reported its terminal state. */
    static void releaseIfReleased(ModuleRecord rec) {
        if (rec.released && !rec.running()) {
            closeLoader(rec);
        }
    }

    private static void closeLoader(ModuleRecord rec) {
        rec.instance = null;
        rec.entry = null;
        if (rec.loader != null) {
            if (rec.loader instanceof java.io.Closeable) {
                ModuleStore.closeQuietly((java.io.Closeable) rec.loader);
            }
            rec.loader = null;
        }
        if (rec.sharedLoader != null) {
            if (rec.sharedLoader instanceof java.io.Closeable) {
                ModuleStore.closeQuietly((java.io.Closeable) rec.sharedLoader);
            }
            rec.sharedLoader = null;
        }
    }

    /** Re-check modules that failed due to missing dependencies, in case a JAR was just added. */
    private void recheckDependents() {
        if (api == null) return;
        List<ModuleRecord> snapshot;
        synchronized (lock) {
            snapshot = new ArrayList<ModuleRecord>(records);
        }
        for (ModuleRecord rec : snapshot) {
            // Only recheck modules that are in ERROR state due to missing dependency
            if (rec.state == ModuleInfo.STATE_ERROR && rec.message != null &&
                rec.message.contains("missing dependency")) {
                // Re-prepare with current shared library loader
                Context context = api.context();
                if (context != null) {
                    String err = prepareModule(context, rec, getSharedLibraryLoaderLocked());
                    if (err == null) {
                        Log.e(TAG, "Dependency resolved, re-prepared: " + rec.path);
                        synchronized (lock) {
                            rec.state = ModuleInfo.STATE_IDLE;
                            rec.message = null;
                        }
                        if (rec.autostart && rec.type != ModuleType.JAR
                                && rec.type != ModuleType.DEX) {
                            run(rec.path);
                        }
                        changed();
                    }
                }
            }
        }
    }

    /** Preferences name, kept public for the test suite. */
    static String prefsName() {
        return PREFS;
    }

    static String describe(Throwable t) {
        if (t == null) {
            return "?";
        }
        Throwable cause = t.getCause();
        if (cause != null) {
            t = cause;
        }
        String msg = t.getMessage();
        return msg == null || msg.length() == 0 ? t.getClass().getName() : msg;
    }
}