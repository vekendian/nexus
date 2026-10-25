package org.vekendian.nexus.api;

import android.content.Context;
import android.net.Uri;

import java.util.List;

/**
 * Implemented by the Extension Registry, the built-in module. The host detects it
 * with {@code instanceof} and drives it; when the module is missing or broken
 * the EXTENSIONS tab falls back to showing the failure on its own card.
 *
 * <p>Asymmetric on purpose. The host hands the executor an {@link ExtensionApi} via
 * the ordinary entry-class lifecycle ({@code onLoad}), and from then on the
 * executor owns everything below: importing extensions into clean storage, loading
 * their dexes, running them on threads, and reporting state back. The host only
 * ever asks questions and draws cards.
 *
 * <p>Methods are called from the main thread except where noted. The executor
 * must not block in {@link #extensions()} -- it snapshots state under a lock.
 */
public interface NexusExecutor {

    /** Snapshot for rendering. Ordered as imported. Never null. */
    List<ExtensionInfo> extensions();

    /**
     * Imports a picked document into {@code files/extensions/<sanitised>.lua|.jar} and
     * registers it. Does not start it.
     *
     * @return the extension id (its path), or null when the document could not be
     *         read or the file has no valid extension type.
     */
    String add(Context context, Uri uri);

    /**
     * Stops the extension if running, deletes its file, unregisters it, and
     * releases the persistable URI grant.
     *
     * @return true when an extension was actually removed.
     */
    boolean remove(String id);

    /**
     * Starts the extension's {@code run()} on its own thread.
     *
     * @return false when the id is unknown or the extension is already running.
     */
    boolean run(String id);

    /** Interrupts a running extension. No-op when it is not running. */
    void stop(String id);

    /** Starts every autostart extension that is not running. */
    void runAll();

    /** Interrupts every running extension. Used when Nexus powers the interface off. */
    void stopAll();

    /** Reason the executor itself could not start, or null when healthy. */
    String failure();

    /**
     * Returns the shared ClassLoader for a {@link ExtensionType#JAR} extension,
     * or null if no such extension is loaded or it is not a JAR.
     *
     * @param extensionId the extension id (filename without .lua/.jar, e.g. "eclipse")
     * @return the shared ClassLoader, or null
     */
    ClassLoader loadLibrary(String extensionId);

    /**
     * Loads an extension and returns its Lua table (for require()).
     *
     * @param extensionId the extension id (filename without .lua/.jar)
     * @return the extension's Lua table, or null
     */
    Object loadExtension(String extensionId);

    /**
     * Returns the export records for a JAR or DEX extension.
     *
     * @param extensionId the extension id (filename without .jar/.dex)
     * @return array of "name\tparams\treturn" records, or empty array if not a JAR/DEX
     *         or has no @Export methods
     */
    String[] jarSpec(String extensionId);

    /**
     * Invokes an exported method on a JAR or DEX extension.
     *
     * @param extensionId the extension id (filename without .jar/.dex)
     * @param method the method name
     * @param packedArgs tab-joined arguments, escaped (see protocol)
     * @return envelope: {"r", value} for success, {"e", message} for error
     */
    String[] jarInvoke(String extensionId, String method, String packedArgs);

    /**
     * Returns the source code of a Lua extension.
     *
     * @param extensionId the extension id (filename without .lua)
     * @return single-element array with source, or empty array if not a Lua extension
     */
    String[] luaSource(String extensionId);
}