package org.vekendian.nexus.api;

import android.app.Activity;
import android.content.Context;

/**
 * What a module (loaded by the module system) is handed when it starts.
 *
 * <p>Deliberately small. This is <em>not</em> a re-implementation of GG's
 * {@code gg.*} Lua API: a script runs inside Nexus's process with the app
 * classloader as its parent, so it can already reach {@code android.ext.*}
 * classes directly (MainService, Tools, Script) if its author is willing to
 * depend on obfuscated names that move between GG releases. This interface is
 * the part that is ours to keep stable.
 *
 * <p>Every method is safe to call from a script thread except {@link #toast},
 * which marshals to the main thread itself.
 */
public interface ModuleApi {

    /** The application context. Never null. */
    Context context();

    /**
     * The host activity, or null when Nexus has no activity up (its window is
     * destroyed but the process lives). Treat it as optional: use it for
     * dialogs, not for anything a script depends on surviving.
     */
    Activity activity();

    /** Writes to logcat under the tag {@code NexusMod}. */
    void log(String message);

    /** A toast, marshalled to the main thread. Ignored when no activity is up. */
    void toast(String message);

    /** Absolute path of the directory modules are imported into. */
    String modulesDir();

    /** Nexus version, from the manifest. */
    String appVersion();

    /**
     * Called after the executor's module list or state changes off the UI
     * thread, so the MODULES tab can repaint. Safe to call from any thread;
     * the host marshals to the main thread itself.
     */
    void modulesChanged();

    /**
     * Returns the shared ClassLoader for a JAR module, or null if no such
     * module is loaded or it is not a JAR.
     *
     * <p>Use this to access classes exported by JAR modules via reflection:
     * <pre>
     * ClassLoader cl = api.getModuleClassLoader("eclipse");
     * if (cl != null) {
     *     Class<?> overlay = cl.loadClass("org.vaelynth.eclipse.EclipseOverlay");
     *     // use via reflection or cast if module-api has the interface
     * }
     * </pre>
     *
     * @param moduleId the module id (filename without .lua/.jar, e.g. "eclipse")
     * @return the shared ClassLoader, or null
     */
    ClassLoader getModuleClassLoader(String moduleId);

    /**
     * Loads a module and returns its Lua table (for require()).
     *
     * @param moduleId the module id (filename without .lua/.jar)
     * @return the module's Lua table, or null
     */
    Object loadModule(String moduleId);
}