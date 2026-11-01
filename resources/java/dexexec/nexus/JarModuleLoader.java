package nexus;

import android.content.Context;
import android.util.Log;

import org.vekendian.nexus.api.ModuleApi;
import org.vekendian.nexus.api.ModuleInfo;
import org.vekendian.nexus.api.ModuleManifest;
import org.vekendian.nexus.api.ModuleType;

import java.io.File;
import java.io.FileInputStream;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.jar.JarFile;

/**
 * Loads JAR modules: one DexClassLoader per .jar, published as a class
 * library.
 *
 * <p>A JAR module is a .jar file containing Java classes. Its classes are
 * exposed to Lua via LuaJava, and to other modules through dependsOn; there
 * is no run() -- JAR modules are libraries, not runnable scripts, so their
 * card shows metadata only, with Remove as the one action.
 *
 * <p>An entry class exists when the archive carries a class annotated with
 * {@code @ModuleManifest}. prepare() finds it itself -- see
 * {@link #discoverEntryByManifest} -- because the manifest is the only place a
 * fresh import could name its entry class, and no caller hands one in. When no
 * class carries a manifest, the JAR loads as a plain class library, which is
 * the historical valid case. The historical -- worse -- fallback by name was
 * removed long ago: it resolved to the engine's own class through parent-first
 * loading, making every entry-less JAR die with "entry class resolved outside
 * the module loader". Discovery by annotation cannot make that mistake.
 */
final class JarModuleLoader {

    private static final String TAG = "NexusMod";

    private JarModuleLoader() {
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
            ModuleStore.closeQuietly(in);
        }
    }

    /**
     * Creates the classloader for a JAR module and reads its metadata.
     *
     * <p>An entry class is required only when {@code entryOverride} names one.
     * Without it the JAR is still valid: it is a class library for other
     * modules, which is what the same loader is published as.
     *
     * @return null on success, or the reason it failed
     */
    static String prepare(Context context, ModuleRecord rec, ClassLoader sharedLibraryLoader) {
        File f = new File(rec.path);
        if (!f.isFile()) {
            return fail(rec, "file is gone");
        }
        // Validate by type: JAR needs ZIP magic, DEX needs dex magic
        if (rec.type == ModuleType.DEX) {
            if (!isDex(f)) {
                return fail(rec, "not a valid .dex file");
            }
        } else {
            if (!isJar(f)) {
                return fail(rec, "not a valid .jar file");
            }
        }
        try {
            // Parent is the shared-library chain when dependencies are loaded,
            // else this dex's classloader. One loader per JAR serves both this
            // module and any other that depends on it.
            ClassLoader parent = sharedLibraryLoader != null ? sharedLibraryLoader : JarModuleLoader.class.getClassLoader();
            rec.loader = new dalvik.system.DexClassLoader(
                    f.getAbsolutePath(),
                    context.getDir("dex", Context.MODE_PRIVATE).getAbsolutePath(),
                    null,
                    parent);

            // A fresh import has no entry name yet: the entry class is
            // whoever in the archive carries @ModuleManifest. Discovery is
            // metadata work -- the archive's own class list, loaded through
            // this module's loader -- and a null result is not an error:
            // an entry-less JAR stays a plain class library.
            if (rec.entryOverride == null || rec.entryOverride.length() == 0) {
                rec.entryOverride = discoverEntryByManifest(context, rec);
            }

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
                rec.name = rec.id();
            }
            if (rec.description == null) {
                rec.description = "";
            }

            // JAR/DEX modules don't have run() - they are libraries
            rec.exported = true;
            // The same loader is what dependents (dependsOn) and LuaJava see.
            rec.sharedLoader = rec.loader;

            return null;
        } catch (Throwable t) {
            return fail(rec, describe(t));
        }
    }

    /** Reads the @ModuleManifest annotation reflectively, by its type NAME. */
    private static String readMeta(Class<?> type, ModuleRecord rec) {
        try {
            for (java.lang.annotation.Annotation a : type.getAnnotations()) {
                if (!"org.vekendian.nexus.api.ModuleManifest".equals(a.annotationType().getName())) {
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
                    rec.type = (ModuleType) typeVal;
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
            return "cannot read @ModuleManifest annotation";
        }
        return "missing @ModuleManifest annotation";
    }

    /**
     * Finds the archive's manifest class without running any of its code.
     *
     * <p>A DexClassLoader cannot enumerate its own classes, so the archive is
     * opened a second time, read-only, purely for its class-name list
     * ({@code DexFile.loadDex} takes both a jar and a raw dex). Each name is
     * then loaded through the module's own loader -- the same loader
     * {@code entryOverride} resolution will use, so the parent-first guard
     * downstream sees a consistent story -- and the first class that carries
     * {@code @ModuleManifest} wins.
     *
     * <p>Nothing here initializes user code: {@code loadClass} loads and
     * links, and static initializers wait for newInstance() in prepare().
     * Inner and anonymous classes ({@code $} in the name) are skipped -- a
     * manifest is a top-level declaration by convention, and loading every
     * inner class of an arbitrary archive is exactly the kind of work a
     * hostile file could make expensive. The budget bounds even the
     * top-level list.
     *
     * @return the manifest class's binary name, or null when the archive
     *         carries no manifest (a plain library JAR -- still valid)
     */
    private static String discoverEntryByManifest(Context context, ModuleRecord rec) {
        dalvik.system.DexFile dex = null;
        try {
            File f = new File(rec.path);
            String opt = context.getDir("dex", Context.MODE_PRIVATE).getAbsolutePath()
                    + File.separator + "meta-" + f.getName() + ".odex";
            dex = dalvik.system.DexFile.loadDex(f.getAbsolutePath(), opt, 0);
            java.util.Enumeration<String> names = dex.entries();
            int budget = 128;
            while (names.hasMoreElements() && budget-- > 0) {
                String name = names.nextElement();
                if (name == null || name.length() == 0 || name.indexOf('$') >= 0) {
                    continue;
                }
                Class<?> type;
                try {
                    type = rec.loader.loadClass(name);
                } catch (Throwable t) {
                    continue;
                }
                if (type.isAnnotationPresent(ModuleManifest.class)) {
                    return name;
                }
            }
            return null;
        } catch (Throwable t) {
            Log.e(TAG, "entry discovery failed for " + rec.path + ": " + t);
            return null;
        } finally {
            if (dex != null) {
                try {
                    dex.close();
                } catch (Throwable ignored) {
                }
            }
        }
    }

    /** Checks that {@code f} is a Dalvik-dex file (starts with the dex magic). */
    static boolean isDex(File f) {
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
            return magic[0] == 'd' && magic[1] == 'e' && magic[2] == 'x' && magic[3] == '\n';
        } catch (Throwable t) {
            return false;
        } finally {
            ModuleStore.closeQuietly(in);
        }
    }

    /** Drops a half-built loader so a rejected module does not leak it. */
    private static String fail(ModuleRecord rec, String why) {
        if (rec.name == null || rec.name.length() == 0) {
            rec.name = rec.id();
        }
        closeLoader(rec);
        return why;
    }

    private static void closeLoader(ModuleRecord rec) {
        rec.instance = null;
        rec.entry = null;
        if (rec.loader != null) {
            if (rec.loader instanceof java.io.Closeable) {
                ModuleStore.closeQuietly((java.io.Closeable) rec.loader);
            }
            rec.loader = null;
        }
        if (rec.sharedLoader != null) {
            if (rec.sharedLoader instanceof java.io.Closeable) {
                ModuleStore.closeQuietly((java.io.Closeable) rec.sharedLoader);
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