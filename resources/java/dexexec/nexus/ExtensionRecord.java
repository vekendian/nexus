package nexus;

import org.vekendian.nexus.api.ExtensionInfo;
import org.vekendian.nexus.api.ExtensionManifest;
import org.vekendian.nexus.api.ExtensionType;

/**
 * One extension: where it is, what its entry class calls, and how it is doing.
 *
 * <p>State fields are volatile because the UI reads them while the extension
 * thread reports terminal state. Structural fields (loader, entry, instance)
 * are published before the thread starts; the executor's lock guards the
 * record list and terminal transitions.
 */
final class ExtensionRecord {

    /** Absolute path of the imported extension. Doubles as the extension id. */
    final String path;

    String name = "";
    String description = "";
    int version;
    boolean autostart = true;

    volatile int state = ExtensionInfo.STATE_IDLE;
    volatile String message;

    ClassLoader loader;
    Class<?> entry;
    Object instance;

    volatile Thread thread;

    /** Set by stop() so an extension can tell "interrupted" from "crashed". */
    volatile boolean stopRequested;

    /** Set when the extension is being removed; the loader closes after the thread ends. */
    volatile boolean released;

    // --- JAR extension support ---

    /** Extension type: LUA (default), JAR. */
    ExtensionType type = ExtensionType.LUA;

    /** Extension IDs this extension depends on (filenames without .lua/.jar). */
    String[] dependsOn = {};

    /** True for JAR extensions: this extension exports classes. */
    boolean exported = false;

    /** Shared classloader for JAR extensions (null for others). */
    ClassLoader sharedLoader;

    /** Override entry class name from @ExtensionManifest.entry() */
    String entryOverride;

    /** Cached export records for JAR/DEX entry class (lazy, set by buildJarSpec). */
    String[] exportedMethods;

    ExtensionRecord(String path) {
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

    ExtensionInfo info() {
        return new ExtensionInfo(path, name, description, version, state, message,
                size(), autostart, type(), dependsOn);
    }

    /** Extension type for ExtensionInfo. */
    ExtensionInfo.Type type() {
        switch (type) {
            case JAR: return ExtensionInfo.Type.JAR;
            case DEX: return ExtensionInfo.Type.DEX;
            default:  return ExtensionInfo.Type.LUA;
        }
    }

    /** The path relative to the extensions directory, for card text. */
    String label() {
        int slash = path.lastIndexOf('/');
        return slash < 0 ? path : path.substring(slash + 1);
    }
}