package nexus;

/**
 * Turns a picked document's name into a file name.
 *
 * <p>Kept apart from {@link nexus.ModuleStore} for one reason: it is the only part of
 * the engine that is pure Java with no Android imports, which means a test can
 * compile and run it and assert on actual output instead of on the shape of the
 * source. File names are the one thing here a user sees directly in the
 * filesystem, so they are worth testing for real.
 *
 * <p>The rules for {@link #sanitise}:
 * <ul>
 *   <li>the module is dropped -- it is a label rule, and the caller decides
 *       whether a suffix belongs on the stored file (see {@link #storedName});
 *   </li>
 *   <li>anything outside {@code [A-Za-z0-9._-]} collapses to a single
 *       underscore, so "My Module  v2.apk" does not become "My__Module__v2";</li>
 *   <li>leading and trailing separators are trimmed;</li>
 *   <li>the result is capped, and a name that sanitises away to nothing becomes
 *       "module" rather than ".dex".</li>
 * </ul>
 */
final class Name {

    static final int MAX_BASE = 48;

    private Name() {
    }

    /** The file-name base for a document called {@code name}. Never empty. */
    static String sanitise(String name) {
        String in = name == null ? "" : name;
        // Basename first. A SAF display name is a bare file name, but a content
        // Uri's last path segment is often "primary:Download/foo.zip" -- turning
        // that into "primary_Download_foo" would put the storage path in the
        // user's modules folder.
        int slash = in.lastIndexOf('/');
        if (slash >= 0) {
            in = in.substring(slash + 1);
        }
        int cut = in.lastIndexOf('.');
        if (cut >= 0) {
            in = in.substring(0, cut);
        }
        StringBuilder sb = new StringBuilder();
        boolean lastUnderscore = false;
        for (int i = 0; i < in.length() && sb.length() < MAX_BASE; i++) {
            char c = in.charAt(i);
            boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
                    || (c >= '0' && c <= '9') || c == '.' || c == '-' || c == '_';
            if (ok) {
                sb.append(c);
                lastUnderscore = false;
            } else if (!lastUnderscore) {
                sb.append('_');
                lastUnderscore = true;
            }
        }
        String out = sb.toString();
        while (out.length() > 0 && isEdge(out.charAt(0))) {
            out = out.substring(1);
        }
        while (out.length() > 0 && isEdge(out.charAt(out.length() - 1))) {
            out = out.substring(0, out.length() - 1);
        }
        return out.length() == 0 ? "module" : out;
    }

    private static boolean isEdge(char c) {
        return c == '_' || c == '.' || c == '-';
    }

    /**
     * The stored file name for a document called {@code name}: the sanitised
     * base plus the document's own extension back again, because the suffix is
     * what {@link nexus.ModuleRegistry} keys type detection on. {@code
     * sanitise} strips the extension as a label rule; storing {@code mymod.lua}
     * under the base {@code mymod} would make {@code add()} read "unknown
     * module type" and reject every install.
     *
     * <p>The suffix comes back only when it looks like one -- a leading dot and
     * one to four letters or digits, e.g. {@code .lua}, {@code .jar}, {@code
     * .LUA}. That keeps a picked {@code foo.zip} (rejected later anyway, but
     * stored truthfully) while refusing oddities like {@code mymod.} or a
     * {@code a.b/c} path escape from ever gaining a slash or reaching {@code
     * new File(dir, base + suffix)}. Everything else stores extensionless and
     * is rejected by type detection exactly as before.
     */
    static String storedName(String name) {
        String in = name == null ? "" : name;
        String base = sanitise(in);
        int cut = in.lastIndexOf('.');
        if (cut > 0 && plainSuffix(in, cut)) {
            String ext = in.substring(cut);
            if (!base.endsWith(ext)) {
                return base + ext;
            }
        }
        return base;
    }

    /** True when {@code in.charAt(cut)} starts a ".x{n}" suffix. */
    private static boolean plainSuffix(String in, int cut) {
        int n = in.length() - cut - 1;
        if (n < 1 || n > 4) {
            return false;
        }
        for (int i = cut + 1; i < in.length(); i++) {
            char c = in.charAt(i);
            boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
                    || (c >= '0' && c <= '9');
            if (!ok) {
                return false;
            }
        }
        return true;
    }
}