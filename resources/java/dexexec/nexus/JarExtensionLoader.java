package nexus;

import android.content.Context;
import android.util.Log;

import org.vekendian.nexus.api.ExtensionApi;
import org.vekendian.nexus.api.ExtensionInfo;
import org.vekendian.nexus.api.ExtensionManifest;
import org.vekendian.nexus.api.ExtensionType;

import java.io.File;
import java.io.FileInputStream;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.jar.JarFile;

/**
 * Loads JAR extensions: one DexClassLoader per .jar, published as a class
 * library.
 *
 * <p>A JAR extension is a .jar file containing Java classes. Its classes are
 * exposed to Lua via LuaJava, and to other extensions through dependsOn; there
 * is no run() -- JAR extensions are libraries, not runnable scripts, so their
 * card shows metadata only, with Remove as the one action.
 *
 * <p>An entry class exists only when a manifest has declared one in
 * {@code entryOverride}; until such a manifest is read before prepare() runs,
 * that is always null, and the JAR loads as a plain library. The historical
 * fallback name resolved to the engine's own class through parent-first
 * loading, which made every entry-less JAR die with
 * "entry class resolved outside the module loader" -- that is why there is no
 * fallback.
 */
final class JarExtensionLoader {

    private static final String TAG = "NexusMod";

    private JarExtensionLoader() {
    }

    /**
     * Checks that {@code f} is a valid JAR file.
     */
    static boolean isJar(File f) {
        if (f == null || !f.isFile() || f.length() < 4) {
            return false;
        }
        FileInputStream in = null;
        try {
            in = new FileInputStream(f);
            byte[] magic = new byte[4];
            int n = 0;
            while (n < magic.length) {
                int r = in.read(magic, n, magic.length - n);
                if (r <= 0) {
                    return false;
                }
                n += r;
            }
            // JAR files start with PK (ZIP magic)
            return magic[0] == 'P' && magic[1] == 'K';
        } catch (Throwable t) {
            return false;
        } finally {
            ExtensionStore.closeQuietly(in);
        }
    }

    /**
     * Creates the classloader for a JAR extension and reads its metadata.
     *
     * <p>An entry class is required only when {@code entryOverride} names one.
     * Without it the JAR is still valid: it is a class library for other
     * extensions, which is what the same loader is published as.
     *
     * @return null on success, or the reason it failed
     */
    static String prepare(Context context, ExtensionRecord rec, ClassLoader sharedLibraryLoader) {
        File f = new File(rec.path);
        if (!f.isFile()) {
            return fail(rec, "file is gone");
        }
        if (!isJar(f)) {
            return fail(rec, "not a valid .jar file");
        }
        try {
            // Parent is the shared-library chain when dependencies are loaded,
            // else this dex's classloader. One loader per JAR serves both this
            // extension and any other that depends on it.
            ClassLoader parent = sharedLibraryLoader != null ? sharedLibraryLoader : JarExtensionLoader.class.getClassLoader();
            rec.loader = new dalvik.system.DexClassLoader(
                    f.getAbsolutePath(),
                    context.getDir("dex", Context.MODE_PRIVATE).getAbsolutePath(),
                    null,
                    parent);

            if (rec.entryOverride != null && rec.entryOverride.length() > 0) {
                Class<?> type;
                try {
                    type = rec.loader.loadClass(rec.entryOverride);
                } catch (ClassNotFoundException e) {
                    return fail(rec, "entry class not found: " + rec.entryOverride);
                }
                // Parent-first loading must not let an entry class resolve to a
                // class the engine itself ships: that would hand Lua an object
                // the user's JAR does not own.
                if (type.getClassLoader() != rec.loader) {
                    return fail(rec, "entry class resolved outside the module loader");
                }
                rec.entry = type;
                // Metadata is optional even with an entry class: a declared
                // entry falls back to the file label rather than rejecting the
                // import, because the classes are usable either way.
                String metaErr = readMeta(type, rec);
                if (metaErr != null) {
                    Log.e(TAG, "manifest metadata ignored for " + rec.path + ": " + metaErr);
                }
                try {
                    rec.instance = type.newInstance();
                } catch (Throwable t) {
                    return fail(rec, "entry class has no usable constructor: " + describe(t));
                }
            }

            if (rec.name == null || rec.name.length() == 0) {
                rec.name = rec.label();
            }
            if (rec.description == null) {
                rec.description = "";
            }

            // JAR extensions don't have run() - they are libraries
            rec.type = ExtensionType.JAR;
            rec.exported = true;
            // The same loader is what dependents (dependsOn) and LuaJava see.
            rec.sharedLoader = rec.loader;

            return null;
        } catch (Throwable t) {
            return fail(rec, describe(t));
        }
    }

    /** Reads the @ExtensionManifest annotation reflectively, by its type NAME. */
    private static String readMeta(Class<?> type, ExtensionRecord rec) {
        try {
            for (java.lang.annotation.Annotation a : type.getAnnotations()) {
                if (!"org.vekendian.nexus.api.ExtensionManifest".equals(a.annotationType().getName())) {
                    continue;
                }
                Class<?> at = a.annotationType();
                rec.name = (String) at.getMethod("name").invoke(a);
                rec.description = (String) at.getMethod("description").invoke(a);
                rec.version = ((Integer) at.getMethod("version").invoke(a)).intValue();
                rec.autostart = ((Boolean) at.getMethod("autostart").invoke(a)).booleanValue();
                // Read new fields
                Object typeVal = at.getMethod("type").invoke(a);
                if (typeVal != null) {
                    rec.type = (ExtensionType) typeVal;
                }
                Object dependsOnVal = at.getMethod("dependsOn").invoke(a);
                if (dependsOnVal != null) {
                    rec.dependsOn = (String[]) dependsOnVal;
                }
                Object entryVal = at.getMethod("entry").invoke(a);
                if (entryVal != null) {
                    String entry = (String) entryVal;
                    if (entry != null && !entry.isEmpty()) {
                        rec.entryOverride = entry;
                    }
                }
                return null;
            }
        } catch (Throwable t) {
            Log.e(TAG, "annotation read failed on " + type.getName() + ": " + t);
            return "cannot read @ExtensionManifest annotation";
        }
        return "missing @ExtensionManifest annotation";
    }

    /** Drops a half-built loader so a rejected extension does not leak it. */
    private static String fail(ExtensionRecord rec, String why) {
        if (rec.name == null || rec.name.length() == 0) {
            rec.name = rec.label();
        }
        closeLoader(rec);
        return why;
    }

    private static void closeLoader(ExtensionRecord rec) {
        rec.instance = null;
        rec.entry = null;
        if (rec.loader != null) {
            if (rec.loader instanceof java.io.Closeable) {
                ExtensionStore.closeQuietly((java.io.Closeable) rec.loader);
            }
            rec.loader = null;
        }
        if (rec.sharedLoader != null) {
            if (rec.sharedLoader instanceof java.io.Closeable) {
                ExtensionStore.closeQuietly((java.io.Closeable) rec.sharedLoader);
            }
            rec.sharedLoader = null;
        }
    }

    static String describe(Throwable t) {
        if (t == null) {
            return "?";
        }
        Throwable cause = t.getCause();
        if (cause != null) {
            t = cause;
        }
        String msg = t.getMessage();
        return msg == null || msg.length() == 0 ? t.getClass().getName() : msg;
    }
}