package org.vekendian.nexus.api;

import android.content.Context;
import android.net.Uri;

import java.util.List;

/**
 * Implemented by the Module Registry, the built-in module. The host detects it
 * with {@code instanceof} and drives it; when the module is missing or broken
 * the MODULES tab falls back to showing the failure on its own card.
 *
 * <p>Asymmetric on purpose. The host hands the executor an {@link ModuleApi} via
 * the ordinary entry-class lifecycle ({@code onLoad}), and from then on the
 * executor owns everything below: importing modules into clean storage, loading
 * their dexes, running them on threads, and reporting state back. The host only
 * ever asks questions and draws cards.
 *
 * <p>Methods are called from the main thread except where noted. The executor
 * must not block in {@link #modules()} -- it snapshots state under a lock.
 */
public interface NexusExecutor {

    /** Snapshot for rendering. Ordered as imported. Never null. */
    List<ModuleInfo> modules();

    /**
     * Imports a picked document into {@code files/modules/<sanitised>.lua|.jar} and
     * registers it. Does not start it.
     *
     * @return the module id (its path), or null when the document could not be
     *         read or the file has no valid extension type.
     */
    String add(Context context, Uri uri);

    /**
     * Stops the module if running, deletes its file, unregisters it, and
     * releases the persistable URI grant.
     *
     * @return true when a module was actually removed.
     */
    boolean remove(String id);

    /**
     * Starts the module's {@code run()} on its own thread.
     *
     * @return false when the id is unknown or the module is already running.
     */
    boolean run(String id);

    /** Interrupts a running module. No-op when it is not running. */
    void stop(String id);

    /** Starts every autostart module that is not running. */
    void runAll();

    /** Interrupts every running module. Used when Nexus powers the interface off. */
    void stopAll();

    /** Reason the executor itself could not start, or null when healthy. */
    String failure();

    /**
     * Returns the shared ClassLoader for a {@link ModuleType#JAR} module,
     * or null if no such module is loaded or it is not a JAR.
     *
     * @param moduleId the module id (filename without .lua/.jar, e.g. "eclipse")
     * @return the shared ClassLoader, or null
     */
    ClassLoader loadLibrary(String moduleId);

    /**
     * Loads a module and returns its Lua table (for require()).
     *
     * @param moduleId the module id (filename without .lua/.jar)
     * @return the module's Lua table, or null
     */
    Object loadModule(String moduleId);

    /**
     * Returns the export records for a JAR or DEX module.
     *
     * @param moduleId the module id (filename without .jar/.dex)
     * @return array of "name\tparams\treturn" records, or empty array if not a JAR/DEX
     *         or has no @Export methods
     */
    String[] jarSpec(String moduleId);

    /**
     * Invokes an exported method on a JAR or DEX module.
     *
     * @param moduleId the module id (filename without .jar/.dex)
     * @param method the method name
     * @param packedArgs tab-joined arguments, escaped (see protocol)
     * @return envelope: {"r", value} for success, {"e", message} for error
     */
    String[] jarInvoke(String moduleId, String method, String packedArgs);

    /**
     * Returns the source code of a Lua module.
     *
     * @param moduleId the module id (filename without .lua)
     * @return single-element array with source, or empty array if not a Lua module
     */
    String[] luaSource(String moduleId);
}