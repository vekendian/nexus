package nexus;

import org.vekendian.nexus.api.ModuleInfo;
import org.vekendian.nexus.api.ModuleManifest;
import org.vekendian.nexus.api.ModuleType;

/**
 * One module: where it is, what its entry class calls, and how it is doing.
 *
 * <p>State fields are volatile because the UI reads them while the module
 * thread reports terminal state. Structural fields (loader, entry, instance)
 * are published before the thread starts; the executor's lock guards the
 * record list and terminal transitions.
 */
final class ModuleRecord {

    /** Absolute path of the imported module. Doubles as the module id. */
    final String path;

    String name = "";
    String description = "";
    int version;
    boolean autostart = true;

    volatile int state = ModuleInfo.STATE_IDLE;
    volatile String message;

    ClassLoader loader;
    Class<?> entry;
    Object instance;

    volatile Thread thread;

    /** Set by stop() so a module can tell "interrupted" from "crashed". */
    volatile boolean stopRequested;

    /** Set when the module is being removed; the loader closes after the thread ends. */
    volatile boolean released;

    // --- JAR module support ---

    /** Module type: LUA (default), JAR. */
    ModuleType type = ModuleType.LUA;

    /** Module IDs this module depends on (filenames without .lua/.jar). */
    String[] dependsOn = {};

    /** True for JAR modules: this module exports classes. */
    boolean exported = false;

    /** Shared classloader for JAR modules (null for others). */
    ClassLoader sharedLoader;

    /** Override entry class name from @ModuleManifest.entry() */
    String entryOverride;

    /** Cached export records for JAR/DEX entry class (lazy, set by buildJarSpec). */
    String[] exportedMethods;

    ModuleRecord(String path) {
        this.path = path;
    }

    long size() {
        java.io.File f = new java.io.File(path);
        return f.isFile() ? f.length() : 0L;
    }

    boolean running() {
        Thread t = thread;
        return t != null && t.isAlive();
    }

    ModuleInfo info() {
        return new ModuleInfo(path, name, description, version, state, message,
                size(), autostart, type(), dependsOn);
    }

    /** Module type for ModuleInfo. */
    ModuleInfo.Type type() {
        switch (type) {
            case JAR: return ModuleInfo.Type.JAR;
            case DEX: return ModuleInfo.Type.DEX;
            default:  return ModuleInfo.Type.LUA;
        }
    }

    /** The path relative to the modules directory, for card text. */
    String label() {
        int slash = path.lastIndexOf('/');
        return slash < 0 ? path : path.substring(slash + 1);
    }

    /** The module's id: its label without the .lua/.jar/.dex suffix. */
    String id() {
        return stripSuffix(label());
    }

    /** Strips a stored file's type suffix from {@code label}. */
    static String stripSuffix(String label) {
        if (label == null) {
            return "";
        }
        if (label.endsWith(".lua") || label.endsWith(".jar")
                || label.endsWith(".dex")) {
            return label.substring(0, label.length() - 4);
        }
        return label;
    }
}