package nexus;

/**
 * Turns a picked document's name into a file name.
 *
 * <p>Kept apart from {@link nexus.ExtensionStore} for one reason: it is the only part of
 * the engine that is pure Java with no Android imports, which means a test can
 * compile and run it and assert on actual output instead of on the shape of the
 * source. File names are the one thing here a user sees directly in the
 * filesystem, so they are worth testing for real.
 *
 * <p>The rules:
 * <ul>
 *   <li>the extension is dropped -- "rish_shizuku.zip" and "rish_shizuku.dex"
 *       must not collide on one target, so the caller always appends .dex;</li>
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
}