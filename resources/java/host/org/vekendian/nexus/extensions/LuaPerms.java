package org.vekendian.nexus.extensions;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Map;

/**
 * Storage for {@link PermRules}: one preference file, read on every call and
 * written only when the user grants something.
 *
 * <p>A denial is never persisted -- the prompt's Deny declines that one call
 * only. Grants are store-only-true, so turning the last checkbox off in the
 * SETTINGS tab (or never checking one) returns the capability to "ask".
 */
final class LuaPerms {

    static final String PREFS = "nexus_perms";

    static final String KEY_PREFIX_GLOBAL = "g:";
    static final String KEY_PREFIX_SCRIPT = "s:";

    private LuaPerms() {
    }

    /** True when any candidate grant for (script, cap) is stored. */
    static boolean allowed(Context context, String script, String cap) {
        SharedPreferences prefs = prefs(context);
        for (String key : PermRules.candidateKeys(script, cap)) {
            if (prefs.getBoolean(key, false)) {
                return true;
            }
        }
        return false;
    }

    /** Remembers one script's "Always allow" for one capability. */
    static void remember(Context context, String script, String cap) {
        prefs(context).edit()
                .putBoolean(PermRules.scriptKey(script, cap), true)
                .apply();
    }

    static boolean global(Context context, String cap) {
        return prefs(context).getBoolean(KEY_PREFIX_GLOBAL + cap, false);
    }

    /**
     * True when at least one script has stored its own answer for a capability.
     *
     * <p>A stored "Always allow" is keyed per script and outranks the global
     * default when the policy is looked up, so the default screen has to know
     * about it: a row that says "Ask" while a script is allowed is a lie the
     * user cannot debug.
     */
    static boolean anyScriptOverride(Context context, String cap) {
        String suffix = ":" + cap;
        for (String key : prefs(context).getAll().keySet()) {
            if (key.startsWith(KEY_PREFIX_SCRIPT) && key.endsWith(suffix)) {
                return true;
            }
        }
        return false;
    }

    static void setGlobal(Context context, String cap, boolean on) {
        SharedPreferences.Editor edit = prefs(context).edit();
        String key = KEY_PREFIX_GLOBAL + cap;
        if (on) {
            edit.putBoolean(key, true);
        } else {
            edit.remove(key);
        }
        edit.apply();
    }

    /**
     * Converts the old broad grants into the individual capability keys the new
     * dialog edits. Without this, a user who once chose "All extension functions"
     * would see five "Ask" rows while still silently being allowed everything.
     */
    static void migrateBroadGrants(Context context) {
        SharedPreferences prefs = prefs(context);
        Map<String, ?> all = prefs.getAll();
        SharedPreferences.Editor edit = prefs.edit();
        boolean changed = false;
        for (Map.Entry<String, ?> entry : all.entrySet()) {
            String key = entry.getKey();
            if (!Boolean.TRUE.equals(entry.getValue())) {
                continue;
            }
            String prefix = null;
            if ("g:*".equals(key) || ("g:" + PermRules.EXTENSIONS_GROUP).equals(key)) {
                prefix = "g:";
            } else if (key.startsWith(KEY_PREFIX_SCRIPT)
                    && (key.endsWith(":" + PermRules.ALL)
                        || key.endsWith(":" + PermRules.EXTENSIONS_GROUP))) {
                prefix = key.substring(0, key.lastIndexOf(':') + 1);
            }
            if (prefix == null) {
                continue;
            }
            for (String cap : PermRules.CAPABILITIES) {
                edit.putBoolean(prefix + cap, true);
            }
            edit.remove(key);
            changed = true;
        }
        if (changed) {
            edit.commit();
        }
    }

    /** Drops every remembered script choice; global grants are untouched. */
    static void clearRemembered(Context context) {
        SharedPreferences prefs = prefs(context);
        SharedPreferences.Editor edit = prefs.edit();
        for (Map.Entry<String, ?> entry : prefs.getAll().entrySet()) {
            if (entry.getKey().startsWith(KEY_PREFIX_SCRIPT)) {
                edit.remove(entry.getKey());
            }
        }
        edit.apply();
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }
}