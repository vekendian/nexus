package org.vekendian.nexus.extensions;

import android.content.Context;

import org.vekendian.nexus.api.ExtensionInfo;
import org.vekendian.nexus.api.NexusExecutor;

import java.io.File;

/**
 * The Java half of the {@code nexus.*} Lua namespace.
 *
 * <p>The Lua-facing tables are built in hand-written smali
 * ({@code org.vekendian.nexus.lua.NexusLua}), because only smali can touch the
 * script environment and GameGuardian's internals. Everything the functions
 * actually do lands here, where javac writes the register frames.
 *
 * <p>The namespace is a registry, not a switch: a call arrives as a full
 * operation name ({@code "extensions.install"}), the part before the first dot
 * selects the category, and one class per category owns the operations below
 * it. Adding a category is one class and one line here -- the Lua table code
 * and the permission model do not change.
 *
 * <p>Every entry point is static and safe to call from a script thread. The
 * permission gate ({@code NexusLua$Perm}) runs before these: nothing here is
 * reached until a call is allowed, and {@link #ready()} is checked first so a
 * script that runs before Nexus starts gets an error instead of a prompt for an
 * operation that could not run anyway.
 */
public final class LuaBridge {

    static final String ERROR_NOT_RUNNING = "extension system is not running";

    private LuaBridge() {
    }

    // ------------------------------------------------- future categories ---

    /**
     * Dispatch table. One entry per category; the key is the Lua subtable name.
     * Today only "extensions" exists, and it is a plain class because Java 8
     * interfaces would still have to be mapped here anyway.
     */
    static Object callCategory(String category, String script, String op, String arg) {
        if ("extensions".equals(category)) {
            return callExtensions(script, op, arg);
        }
        return "unknown function: nexus." + op;
    }

    static Object callExtensions(String script, String op, String arg) {
        Context context = NexusHost.app();
        NexusExecutor executor = NexusHost.executor();
        if (context == null || executor == null) {
            return ERROR_NOT_RUNNING;
        }
        try {
            String fn = op.substring("extensions.".length());
            if ("list".equals(fn)) {
                return LuaExtensions.list(executor);
            }
            String path = arg == null ? "" : arg.trim();
            if (path.length() == 0 || "nil".equals(path)) {
                return "missing extension path";
            }
            if ("install".equals(fn)) {
                return LuaExtensions.install(context, executor, path);
            }
            // Import ops match by extension id ("zip"), not by full path, and
            // return records/envelopes rather than ExtensionInfo objects.
            if ("spec".equals(fn)) {
                return LuaExtensions.spec(executor, path);
            }
            if ("invoke".equals(fn)) {
                // The packed record is escape-sensitive: trimming it would
                // eat a trailing space inside the last argument.
                return LuaExtensions.invoke(executor, arg);
            }
            if ("source".equals(fn)) {
                return LuaExtensions.source(executor, path);
            }
            ExtensionInfo target = LuaExtensions.find(executor, path);
            if (target == null) {
                return "no extension at " + path;
            }
            if ("uninstall".equals(fn)) {
                return LuaExtensions.uninstall(executor, target)
                        ? null : "extension could not be removed";
            }
            return "unknown function: nexus." + op;
        } catch (Throwable t) {
            return ExtensionLoader.describe(t);
        }
    }

    // ------------------------------------------------------ Lua entry points ---

    /** True once the executor is loaded; checked before any prompt or dispatch. */
    public static boolean ready() {
        return NexusHost.app() != null && NexusHost.executor() != null;
    }

    /**
     * Runs one {@code nexus.*} call.
     *
     * @return {@code null} on success, a String error to return as
     *         {@code nil, err}, or a String[] of tab-separated records that the
     *         Lua side turns into a table ({@code extensions.list}).
     */
    public static Object call(String script, String op, String arg) {
        if (op == null) {
            return "unknown function";
        }
        int dot = op.indexOf('.');
        if (dot <= 0) {
            return "unknown function: nexus." + op;
        }
        return callCategory(op.substring(0, dot), script, op, arg);
    }

    // ---------------------------------------------------------- permission ---

    /** {@link PermRules#ALLOW} when the call needs no prompt, else ASK. */
    public static int policy(String script, String cap) {
        Context context = NexusHost.app();
        if (context == null) {
            return PermRules.ASK;
        }
        return LuaPerms.allowed(context, script, cap)
                ? PermRules.ALLOW : PermRules.ASK;
    }

    /** "Always allow": remembered for this script and capability. */
    public static void remember(String script, String cap) {
        Context context = NexusHost.app();
        if (context != null) {
            LuaPerms.remember(context, script, cap);
        }
    }

    /** Capability names for the SETTINGS permissions screen. */
    public static String[] capabilities() {
        return PermRules.CAPABILITIES.clone();
    }

    public static boolean global(String cap) {
        Context context = NexusHost.app();
        return context != null && LuaPerms.global(context, cap);
    }

    public static void setGlobal(String cap, boolean on) {
        Context context = NexusHost.app();
        if (context != null) {
            LuaPerms.setGlobal(context, cap, on);
        }
    }

    /**
     * True when some script has answered for itself on this capability.
     *
     * <p>A stored "Always allow" outranks the global default, so a row that
     * says "Ask" can be wrong about the script the user is thinking of. The
     * row has to say so rather than quietly disagree with the prompt.
     */
    public static boolean scriptOverride(String cap) {
        Context context = NexusHost.app();
        return context != null && LuaPerms.anyScriptOverride(context, cap);
    }

    /** Converts old broad grants before the per-capability dialog reads them. */
    public static void migrateBroadGrants() {
        Context context = NexusHost.app();
        if (context != null) {
            LuaPerms.migrateBroadGrants(context);
        }
    }

    public static void clearRemembered() {
        Context context = NexusHost.app();
        if (context != null) {
            LuaPerms.clearRemembered(context);
        }
    }

    /**
     * The prompt's message, from a pinned string resource ("Allow %1$s to call
     * %2$s?"). The id arrives from smali because this class is compiled before
     * the resource table exists; the script is shown by file name, not path.
     */
    public static String permMessage(int templateId, String script, String op) {
        Context context = NexusHost.app();
        if (context == null) {
            return op;
        }
        String name = new File(script == null ? "" : script).getName();
        if (name.length() == 0) {
            name = script == null ? "" : script;
        }
        return String.format(context.getString(templateId), name, op);
    }
}