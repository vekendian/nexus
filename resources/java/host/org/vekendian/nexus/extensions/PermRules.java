package org.vekendian.nexus.extensions;

import java.util.ArrayList;
import java.util.Map;
import java.security.MessageDigest;

/**
 * The permission policy behind the {@code nexus.*} Lua namespace, as pure Java.
 *
 * <p>Kept free of Android imports for the same reason as {@code nexus.Name}: it
 * is the part that decides whether a script may act, and a test can compile and
 * run it against real inputs instead of asserting on source text.
 *
 * <p>The model is deliberately one-sided. A capability is either granted (by a
 * remembered per-script choice, an exact global grant, a group grant like
 * {@code extensions.*}, or {@code *}) or it raises the prompt. Denial is never
 * stored, so "why did this stop asking?" always has a visible answer in the
 * SETTINGS tab.
 *
 * <p>Keys live in one preference file:
 * <ul>
 *   <li>{@code g:<capability>} -- global grant from the SETTINGS tab;</li>
 *   <li>{@code s:<sha1(script)>:<capability>} -- "Always allow" from the prompt,
 *       scoped to one script so one script's answer never speaks for another.
 *       The script path is hashed because preference keys cannot sensibly carry
 *       arbitrary filesystem paths.</li>
 * </ul>
 */
final class PermRules {

    static final int ASK = 0;
    static final int ALLOW = 1;

    static final String ALL = "*";
    static final String EXTENSIONS_GROUP = "extensions.*";

    /** Capabilities the floating Settings screen offers individually. Broad
     *  grants still exist as storage keys, but only for migration: the UI writes
     *  the exact capability so one button cannot silently grant everything. */
    static final String[] CAPABILITIES = {
            "extensions.install",
            "extensions.uninstall",
            "extensions.list",
            "extensions.import",
    };

    private PermRules() {
    }

    /**
     * Keys that can grant {@code cap} to {@code script}, most specific first.
     * The order is what makes a script's own answer beat a broad global one.
     */
    static String[] candidateKeys(String script, String cap) {
        ArrayList<String> keys = new ArrayList<String>(4);
        add(keys, scriptKey(script, cap));
        add(keys, "g:" + cap);
        int dot = cap == null ? -1 : cap.indexOf('.');
        if (dot > 0) {
            add(keys, "g:" + cap.substring(0, dot) + ".*");
        }
        add(keys, "g:" + ALL);
        return keys.toArray(new String[0]);
    }

    private static void add(ArrayList<String> keys, String key) {
        if (!keys.contains(key)) {
            keys.add(key);
        }
    }

    static String scriptKey(String script, String cap) {
        return "s:" + digest(script == null ? "" : script) + ":" + cap;
    }

    /** Test seam: whether any candidate key in {@code grants} is true. */
    static boolean granted(Map<String, Boolean> grants, String script, String cap) {
        for (String key : candidateKeys(script, cap)) {
            if (Boolean.TRUE.equals(grants.get(key))) {
                return true;
            }
        }
        return false;
    }

    static String digest(String value) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            byte[] bytes = md.digest(value.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder(bytes.length * 2);
            for (byte b : bytes) {
                sb.append(Character.forDigit((b >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b & 0xF, 16));
            }
            return sb.toString();
        } catch (Exception e) {
            return Integer.toHexString(value.hashCode());
        }
    }
}