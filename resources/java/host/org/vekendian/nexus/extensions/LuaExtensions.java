package org.vekendian.nexus.extensions;

import android.content.Context;
import android.net.Uri;

import org.vekendian.nexus.api.ExtensionInfo;
import org.vekendian.nexus.api.NexusExecutor;

import java.io.File;
import java.util.List;

/**
 * The {@code nexus.extensions.*} category.
 *
 * <p>Thin on purpose: everything below the ids belongs to {@link NexusExecutor},
 * and the executor is the only thing that may touch the extensions. uninstall
 * resolves the argument against the executor's own list first, so a path a
 * script made up cannot reach a file the executor does not own.
 *
 * <p>{@code list} returns tab-separated records rather than ExtensionInfo objects:
 * the Lua side is smali, and picking fields out of a value class there would be
 * both longer and easier to get wrong than splitting five strings.
 */
final class LuaExtensions {

    private LuaExtensions() {
    }

    static String[] list(NexusExecutor executor) {
        List<ExtensionInfo> extensions = executor.extensions();
        String[] records = new String[extensions.size()];
        for (int i = 0; i < records.length; i++) {
            ExtensionInfo s = extensions.get(i);
            records[i] = field(s.path()) + '\t' + field(s.name()) + '\t'
                    + state(s.state()) + '\t' + s.version() + '\t'
                    + (s.autostart() ? "true" : "false");
        }
        return records;
    }

    /** null on success, otherwise the reason for {@code nil, err}. */
    static Object install(Context context, NexusExecutor executor, String path) {
        File file = new File(path);
        if (!file.isFile() || !file.canRead()) {
            return "cannot read " + path;
        }
        try {
            String id = executor.add(context, Uri.fromFile(file));
            return id == null
                    ? "extension could not be imported (not a loadable jar?)"
                    : null;
        } catch (Throwable t) {
            return ExtensionLoader.describe(t);
        }
    }

    // --------------------------------------------------------- import ops ---

    /**
     * The export records of a JAR/DEX extension, or an empty array for a
     * Lua extension (the import builder falls through to {@code source}).
     * Unknown extensions resolve to an error string.
     *
     * <p>{@code id} is the bare extension name ("zip"), matched without
     * suffix, not the full path {@code install/uninstall} accept.
     */
    static Object spec(NexusExecutor executor, String id) {
        if (!known(executor, id)) {
            return "no extension at " + id;
        }
        try {
            return executor.jarSpec(id);
        } catch (Throwable t) {
            return ExtensionLoader.describe(t);
        }
    }

    /**
     * One invoke: {@code packed} is
     * {@code method<TAB>pspec<TAB>escaped-args}, produce of the smali
     * JarsFn wrapper. The envelope the engine returns ({@code "r"/"e"},
     * value) is handed straight back to Lua -- the wrapper re-types by its
     * own return code, this side only relays.
     */
    static Object invoke(NexusExecutor executor, String packed) {
        int method = packed.indexOf('\t');
        int spec = method < 0 ? -1 : packed.indexOf('\t', method + 1);
        int args = spec < 0 ? -1 : packed.indexOf('\t', spec + 1);
        if (method < 0 || spec < 0 || args < 0) {
            return "malformed invoke record";
        }
        String id = packed.substring(0, method);
        String name = packed.substring(method + 1, spec);
        String rest = packed.substring(args + 1, packed.length());
        if (!known(executor, id)) {
            return "no extension at " + id;
        }
        try {
            return executor.jarInvoke(id, name, rest);
        } catch (Throwable t) {
            return ExtensionLoader.describe(t);
        }
    }

    /**
     * The source of a Lua extension as an envelope: {@code {"r", source}} or
     * {@code {"e", reason}}. Empty when the extension is not Lua (the JAR
     * path handled {@code spec}). The import builder loadstrings the value
     * in the caller's own environment.
     */
    static Object source(NexusExecutor executor, String id) {
        if (!known(executor, id)) {
            return "no extension at " + id;
        }
        try {
            return executor.luaSource(id);
        } catch (Throwable t) {
            return ExtensionLoader.describe(t);
        }
    }

    /** True when {@code id} names any registered extension (bare or full path). */
    private static boolean known(NexusExecutor executor, String id) {
        if (id == null || id.length() == 0) {
            return false;
        }
        for (ExtensionInfo s : executor.extensions()) {
            if (id.equals(s.path())) {
                return true;
            }
            String label = s.path();
            int slash = label.lastIndexOf('/');
            if (slash >= 0) {
                label = label.substring(slash + 1);
            }
            int dot = label.lastIndexOf('.');
            if (dot > 0) {
                label = label.substring(0, dot);
            }
            if (id.equals(label)) {
                return true;
            }
        }
        return false;
    }

    /** The registered extension whose id is exactly {@code path}, or null. */
    static ExtensionInfo find(NexusExecutor executor, String path) {
        for (ExtensionInfo s : executor.extensions()) {
            if (path.equals(s.path())) {
                return s;
            }
        }
        return null;
    }

    static boolean uninstall(NexusExecutor executor, ExtensionInfo extension) {
        return executor.remove(extension.path());
    }

    static String state(int state) {
        switch (state) {
            case ExtensionInfo.STATE_RUNNING:
                return "running";
            case ExtensionInfo.STATE_FINISHED:
                return "finished";
            case ExtensionInfo.STATE_STOPPED:
                return "stopped";
            case ExtensionInfo.STATE_ERROR:
                return "error";
            case ExtensionInfo.STATE_IDLE:
            default:
                return "idle";
        }
    }

    /** Tabs and newlines would break the record format. */
    private static String field(String value) {
        if (value == null) {
            return "";
        }
        return value.replace('\t', ' ').replace('\n', ' ');
    }
}