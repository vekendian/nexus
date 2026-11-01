package nexus;

import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.util.Log;

import org.vekendian.nexus.api.ModuleApi;
import org.vekendian.nexus.api.ModuleManifest;
import org.vekendian.nexus.api.ModuleType;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * Where modules live and how one gets there.
 *
 * <p>The clean-path rule, which is the whole reason this class exists: a SAF
 * document is a {@code content://} Uri with an opaque, percent-encoded document
 * id. That path is not a file, it cannot be handed to a DexClassLoader, and it
 * changes if the file is moved. So an import copies the document once into
 * {@code files/modules/<sanitised>.lua|.jar|.dex} and only the copy is ever remembered.
 *
 * <p>State lives in one SharedPreferences file, {@code nexus_modules}, key
 * {@code entries}: newline-separated records in format "path|type|dependsOnCsv".
 * Deliberately not GameGuardian's own prefs file, whose loader is not built to
 * tolerate foreign keys.
 *
 * <p>Backward compatibility: old format (newline-separated paths) is still read,
 * but new entries are written in the new format.
 */
final class ModuleStore {

    private static final String PREFS = "nexus_modules";
    private static final String KEY_ENTRIES = "entries";

    private static final String TAG = "NexusMod";

    private final Context context;
    private final ModuleApi api;

    ModuleStore(Context context, ModuleApi api) {
        this.context = context;
        this.api = api;
    }

    /** One persisted module entry with path, type, and dependencies. */
    static final class Entry {
        final String path;
        final ModuleType type;
        final String[] dependsOn;

        Entry(String path, ModuleType type, String[] dependsOn) {
            this.path = path;
            this.type = type != null ? type : ModuleType.LUA;
            this.dependsOn = dependsOn != null ? dependsOn : new String[0];
        }
    }

    // ------------------------------------------------------------- persistence ---

    /** Returns all valid module entries (path exists). */
    List<Entry> entries() {
        List<Entry> out = new ArrayList<Entry>();
        String raw = prefs().getString(KEY_ENTRIES, "");
        if (raw == null || raw.length() == 0) {
            // Backward compat: try old "paths" key
            raw = prefs().getString("paths", "");
            if (raw == null || raw.length() == 0) {
                return out;
            }
            // Old format: just paths, one per line
            String[] parts = raw.split("\n");
            for (int i = 0; i < parts.length; i++) {
                String p = parts[i].trim();
                if (p.length() > 0 && new File(p).isFile()) {
                    out.add(new Entry(p, ModuleType.LUA, new String[0]));
                }
            }
            // Migrate to new format
            if (!out.isEmpty()) {
                saveEntries(out);
            }
            return out;
        }
        String[] parts = raw.split("\n");
        for (int i = 0; i < parts.length; i++) {
            String line = parts[i].trim();
            if (line.length() == 0) continue;
            String[] fields = line.split("\\|", 3);
            String path = fields[0];
            if (path.length() == 0 || !new File(path).isFile()) {
                continue; // drop missing files
            }
            ModuleType type = ModuleType.LUA;
            String[] dependsOn = new String[0];
            if (fields.length > 1 && fields[1].length() > 0) {
                try {
                    type = ModuleType.valueOf(fields[1]);
                } catch (IllegalArgumentException e) {
                    // default to LUA
                }
            }
            if (fields.length > 2 && fields[2].length() > 0) {
                dependsOn = fields[2].split(",");
            }
            out.add(new Entry(path, type, dependsOn));
        }
        return out;
    }

    /** @deprecated Use entries() instead. */
    @Deprecated
    List<String> paths() {
        List<String> out = new ArrayList<String>();
        for (Entry e : entries()) {
            out.add(e.path);
        }
        return out;
    }

    synchronized void saveEntries(List<Entry> entries) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < entries.size(); i++) {
            Entry e = entries.get(i);
            if (i > 0) sb.append('\n');
            sb.append(e.path).append('|').append(e.type.name());
            if (e.dependsOn.length > 0) {
                sb.append('|');
                for (int j = 0; j < e.dependsOn.length; j++) {
                    if (j > 0) sb.append(',');
                    sb.append(e.dependsOn[j]);
                }
            }
        }
        prefs().edit().putString(KEY_ENTRIES, sb.toString()).commit();
    }

    /** Adds one entry without overwriting a concurrent migration/import. */
    synchronized void addEntry(String path, ModuleType type, String[] dependsOn) {
        List<Entry> entries = entries();
        // Remove existing entry with same path
        for (int i = 0; i < entries.size(); i++) {
            if (entries.get(i).path.equals(path)) {
                entries.remove(i);
                break;
            }
        }
        entries.add(new Entry(path, type, dependsOn));
        saveEntries(entries);
    }

    /** Removes one entry without rewriting records the caller does not own. */
    synchronized void removePath(String path) {
        List<Entry> entries = entries();
        boolean removed = false;
        for (int i = 0; i < entries.size(); i++) {
            if (entries.get(i).path.equals(path)) {
                entries.remove(i);
                removed = true;
                break;
            }
        }
        if (removed) {
            saveEntries(entries);
        }
    }

    /** True when a persisted record already owns {@code path}. */
    synchronized boolean hasEntry(String path) {
        List<Entry> entries = entries();
        for (int i = 0; i < entries.size(); i++) {
            if (entries.get(i).path.equals(path)) {
                return true;
            }
        }
        return false;
    }

    @Deprecated
    synchronized void addPath(String path) {
        addEntry(path, ModuleType.LUA, new String[0]);
    }

    private SharedPreferences prefs() {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    // ------------------------------------------------------------------ import ---

    /** Where an import ended up, or null when the document could not be read. */
    synchronized File importUri(Uri uri) {
        try {
            return copyUri(uri);
        } finally {
            // The copy is all the executor needs. Holding a persistable grant
            // after that leaks access and survives until the app is uninstalled.
            release(uri);
        }
    }

    /** Drops a persistable read grant, if the provider gave one. */
    void release(Uri uri) {
        if (uri == null) {
            return;
        }
        try {
            context.getContentResolver().releasePersistableUriPermission(
                    uri, android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (Throwable t) {
            // Not every provider grants (or releases) a persistable permission.
            Log.e(TAG, "persistable grant release failed: " + t);
        }
    }

    private File copyUri(Uri uri) {
        String name = displayNameOf(uri);
        // The stored file keeps the document's extension: type detection and
        // both id resolutions key on it. Name.sanitise is a label rule and drops
        // it, so storedName is what hands a ".lua"/".jar"/".dex" through.
        File dir = dir();
        if (!dir.isDirectory() && !dir.mkdirs()) {
            Log.e(TAG, "modules dir not created: " + dir);
            return null;
        }
        String stored = Name.storedName(name);
        File named = new File(dir, stored);
        // A name no record owns is a leftover: a rejected import, or a copy
        // whose record was never written. Reusing it keeps the second install
        // of Eclipse.dex from becoming Eclipse-2.dex; delete(target) below
        // overwrites the stale file.
        File target = hasEntry(named.getAbsolutePath())
                ? uniquePath(dir, stored) : named;
        File tmp = new File(dir, target.getName() + ".part");

        // Hold the read grant across the copy: without it the document becomes
        // unreadable the moment the picker activity finishes.
        try {
            context.getContentResolver().takePersistableUriPermission(
                    uri, android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (Throwable t) {
            // Not fatal. Some providers do not offer persistable grants, and the
            // copy below may still succeed; if it does not, the reason surfaces
            // as an import failure instead of a silent empty script.
            Log.e(TAG, "persistable grant refused: " + t);
        }

        InputStream in = null;
        FileOutputStream out = null;
        try {
            in = context.getContentResolver().openInputStream(uri);
            if (in == null) {
                return null;
            }
            out = new FileOutputStream(tmp);
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
            }
            out.flush();
            out.getFD().sync();
        } catch (Throwable t) {
            Log.e(TAG, "import copy failed: " + t);
            closeQuietly(out);
            closeQuietly(in);
            delete(tmp);
            return null;
        }
        closeQuietly(out);
        closeQuietly(in);

        if (tmp.length() == 0L) {
            delete(tmp);
            return null;
        }
        delete(target);
        if (!tmp.renameTo(target)) {
            Log.e(TAG, "import rename failed: " + tmp);
            delete(tmp);
            return null;
        }
        return target;
    }

    void delete(File f) {
        if (f != null && f.isFile() && !f.delete()) {
            Log.e(TAG, "delete failed: " + f);
        }
    }

    /** The clean-path directory, created on demand. */
    File dir() {
        return new File(api.modulesDir());
    }

    // ----------------------------------------------------------------- naming ---

    /**
     * The document's display name, or its last path segment.
     *
     * <p>DocumentsUI's own _display_name is what the user recognises. Failing
     * that, a document id like {@code primary:Download/Foo.zip} still yields a
     * usable tail; failing even that, "module".
     */
    String displayNameOf(Uri uri) {
        Cursor c = null;
        try {
            c = context.getContentResolver().query(uri,
                    new String[] { "_display_name" }, null, null, null);
            if (c != null && c.moveToFirst()) {
                String n = c.getString(0);
                if (n != null && n.length() > 0) {
                    return n;
                }
            }
        } catch (Throwable t) {
            Log.e(TAG, "display name query failed: " + t);
        } finally {
            if (c != null) {
                try {
                    c.close();
                } catch (Throwable ignored) {
                    // nothing useful to do
                }
            }
        }
        String seg = uri.getLastPathSegment();
        return seg == null || seg.length() == 0 ? "module" : seg;
    }

    /** dir/<base>.lua|.jar, then -2, -3 ... until it is free. */
    private static File uniquePath(File dir, String base) {
        File f = new File(dir, base);
        int n = 1;
        while (f.exists()) {
            n++;
            int dot = base.lastIndexOf('.');
            String name = dot > 0 ? base.substring(0, dot) : base;
            String ext = dot > 0 ? base.substring(dot) : "";
            f = new File(dir, name + "-" + n + ext);
        }
        return f;
    }

    static void closeQuietly(java.io.Closeable c) {
        if (c == null) {
            return;
        }
        try {
            c.close();
        } catch (Throwable ignored) {
            // nothing useful to do
        }
    }
}