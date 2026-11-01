package org.vekendian.nexus.modules;

import android.content.Context;
import android.net.Uri;

import org.vekendian.nexus.api.ModuleInfo;
import org.vekendian.nexus.api.NexusExecutor;

import java.io.File;
import java.util.List;

/**
 * The {@code nexus.modules.*} category.
 *
 * <p>Thin on purpose: everything below the ids belongs to {@link NexusExecutor},
 * and the executor is the only thing that may touch the modules. uninstall
 * resolves the argument against the executor's own list first, so a path a
 * script made up cannot reach a file the executor does not own.
 *
 * <p>{@code list} returns tab-separated records rather than ModuleInfo objects:
 * the Lua side is smali, and picking fields out of a value class there would be
 * both longer and easier to get wrong than splitting five strings.
 */
final class LuaModules {

    private LuaModules() {
    }

    static String[] list(NexusExecutor executor) {
        List<ModuleInfo> modules = executor.modules();
        String[] records = new String[modules.size()];
        for (int i = 0; i < records.length; i++) {
            ModuleInfo s = modules.get(i);
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
                    ? "module could not be imported (expected .lua, .jar or .dex)"
                    : null;
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
        }
    }

    // --------------------------------------------------------- import ops ---

    /**
     * The export records of a JAR/DEX module, or an empty array for a
     * Lua module (the import builder falls through to {@code source}).
     * Unknown modules resolve to an error string.
     *
     * <p>{@code id} is the bare module name ("zip"), matched without
     * suffix, not the full path {@code install/uninstall} accept.
     */
    static Object spec(NexusExecutor executor, String id) {
        if (!known(executor, id)) {
            return "no module at " + id;
        }
        try {
            return executor.jarSpec(id);
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
        }
    }

    /**
     * The module's classloader, or null when the module is not a jar/dex
     * (or has none yet). The Lua import builder registers it so
     * {@code luajava} can resolve the module's classes -- that is what turns
     * {@code local probe = nexus.modules.import("probe")} into
     * {@code probe.Probe("hello")}.
     *
     * <p>Null is the ordinary answer for a .lua module and for an unknown
     * id: the builder treats both as "no loader" and keeps its spec-then-source
     * order, so this op never needs an error string of its own.
     */
    static Object loader(NexusExecutor executor, String id) {
        if (!known(executor, id)) {
            return null;
        }
        try {
            return executor.loadLibrary(id);
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
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
            return "no module at " + id;
        }
        try {
            return executor.jarInvoke(id, name, rest);
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
        }
    }

    /**
     * The source of a Lua module as an envelope: {@code {"r", source}} or
     * {@code {"e", reason}}. Empty when the module is not Lua (the JAR
     * path handled {@code spec}). The import builder loadstrings the value
     * in the caller's own environment.
     */
    static Object source(NexusExecutor executor, String id) {
        if (!known(executor, id)) {
            return "no module at " + id;
        }
        try {
            return executor.luaSource(id);
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
        }
    }

    /** True when {@code id} names any registered module (bare or full path). */
    private static boolean known(NexusExecutor executor, String id) {
        if (id == null || id.length() == 0) {
            return false;
        }
        for (ModuleInfo s : executor.modules()) {
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

    /** The registered module whose id is exactly {@code path}, or null. */
    static ModuleInfo find(NexusExecutor executor, String path) {
        for (ModuleInfo s : executor.modules()) {
            if (path.equals(s.path())) {
                return s;
            }
        }
        return null;
    }

    static boolean uninstall(NexusExecutor executor, ModuleInfo module) {
        return executor.remove(module.path());
    }

    static String state(int state) {
        switch (state) {
            case ModuleInfo.STATE_RUNNING:
                return "running";
            case ModuleInfo.STATE_FINISHED:
                return "finished";
            case ModuleInfo.STATE_STOPPED:
                return "stopped";
            case ModuleInfo.STATE_ERROR:
                return "error";
            case ModuleInfo.STATE_IDLE:
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