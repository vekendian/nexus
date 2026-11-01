package org.vekendian.nexus.modules;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import org.vekendian.nexus.api.ModuleManifest;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.annotation.Annotation;
import java.lang.reflect.Method;

/**
 * Turns the Module Registry's .dex asset into a live {@link
 * ModuleRegistry}.
 *
 * <p>Three steps, each of which has bitten this project before, so each is
 * spelled out rather than folded together:
 *
 * <ol>
 *   <li><b>Extract</b> the asset. A raw resource is not a usable dex path, and
 *       reading it out of the APK on every resume is wasteful, so it is copied
 *       once into app-private storage and re-copied only when the asset's length
 *       changes (the length is a cheap proxy for "the app was upgraded").
 *   <li><b>Point a classloader at the extracted file.</b> The parent is the
 *       host's own classloader, so the registry can see ModuleApi, ModuleRegistry
 *       and everything else Nexus ships -- that is what lets it compile against
 *       the API and run at all.
 *   <li><b>Find the entry class</b> by its unique name
 *       ({@code nexus.ModuleRegistry}) and read its {@link ModuleManifest} annotation
 *       reflectively. Reflection, not a cast: the annotation type lives in the
 *       host dex but the annotated class lives in the asset dex, and
 *       {@code getAnnotation()} hands back the right type either way, whereas a
 *       direct reference would force the compiler to tie the two together.
 * </ol>
 */
final class ModuleLoader {

    /** Where the asset lands. "dexexec" rather than "modules": modules/ holds
     *  the user's modules, which the registry manages and this must not touch. */
    private static final String ASSET_DIR = "dexexec";
    private static final String ASSET_NAME = "nexus_dexexec.dex";
    private static final String STATE_PREFS = "nexus_dexexec_asset";
    private static final String STATE_KEY = "length";

    /** The registry's private entry name. It must not collide with a user
     *  module's entry class ({@code entry}/{@code nexus.entry}). */
    static final String[] ENTRIES = { "nexus.ModuleRegistry" };

    /** What the annotation said. Defaults are what a module with no annotation
     *  gets: its file's name is filled in by the caller. */
    static final class Meta {
        String name = "";
        String description = "";
        int version;
        boolean autostart = true;
    }

    private ModuleLoader() {
    }

    /**
     * Copies the raw asset out if it is missing or stale.
     *
     * @return the extracted dex file, or null when the asset could not be read
     */
    static File extract(Context context, int rawId) {
        if (context == null || rawId == 0) {
            return null;
        }
        File dir = context.getDir(ASSET_DIR, Context.MODE_PRIVATE);
        if (!dir.isDirectory() && !dir.mkdirs()) {
            Log.e(NexusHost.TAG, "asset dir not created: " + dir);
            return null;
        }
        File out = new File(dir, ASSET_NAME);
        SharedPreferences prefs = context.getSharedPreferences(STATE_PREFS, Context.MODE_PRIVATE);
        long known = prefs.getLong(STATE_KEY, -1L);
        long actual;
        InputStream in = null;
        try {
            in = context.getResources().openRawResource(rawId);
            actual = in.available();
        } catch (Throwable t) {
            Log.e(NexusHost.TAG, "asset open failed: " + t);
            return null;
        }
        // available() is a hint, not a length, for a deflated stream: read the
        // whole thing to a temp file and only then decide. A stale-length skip
        // would leave a truncated dex that fails verification at load time,
        // which is a far worse failure than re-extracting every time.
        File tmp = new File(dir, ASSET_NAME + ".part");
        FileOutputStream fos = null;
        long copied = 0L;
        try {
            fos = new FileOutputStream(tmp);
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) {
                fos.write(buf, 0, n);
                copied += n;
            }
            fos.flush();
            fos.getFD().sync();
        } catch (Throwable t) {
            Log.e(NexusHost.TAG, "asset copy failed: " + t);
            close(fos);
            close(in);
            delete(tmp);
            return null;
        }
        close(fos);
        close(in);
        if (copied == 0L) {
            delete(tmp);
            return null;
        }
        if (out.isFile() && out.length() == copied && known == copied) {
            // Same bytes as last time: keep the existing file (its mtime is
            // what anything downstream might care about) and drop the copy.
            delete(tmp);
            return out;
        }
        if (!tmp.renameTo(out)) {
            // renameTo within one directory should not fail, but if it does the
            // dex still has to land somewhere loadable.
            delete(out);
            if (!tmp.renameTo(out)) {
                Log.e(NexusHost.TAG, "asset rename failed: " + tmp);
                delete(tmp);
                return null;
            }
        }
        prefs.edit().putLong(STATE_KEY, copied).commit();
        Log.e(NexusHost.TAG, "asset extracted: " + out + " (" + copied + " bytes)");
        return out;
    }

    /**
     * Loads the entry class and reads its annotation.
     *
     * @return the instantiated entry object, or null with {@code error} set
     */
    static Object load(Context context, ClassLoader parent, File dex, Meta meta, String[] error) {
        ClassLoader cl = null;
        try {
            cl = new dalvik.system.DexClassLoader(
                    dex.getAbsolutePath(),
                    optimizedDir(context),
                    null,
                    parent);
            Class<?> type = null;
            for (String candidate : ENTRIES) {
                try {
                    type = cl.loadClass(candidate);
                    break;
                } catch (ClassNotFoundException e) {
                    // try the next candidate
                }
            }
            if (type == null) {
                error[0] = "no entry class (looked for " + join(ENTRIES) + ")";
                closeQuietly(cl);
                return null;
            }
            readMeta(type, meta);
            // Keep the loader open: the registry's classes and the loaders it
            // creates are parented to it. Closing it here would break every
            // subsequent module load.
            return type.newInstance();
        } catch (Throwable t) {
            closeQuietly(cl);
            error[0] = describe(t);
            Log.e(NexusHost.TAG, "module load failed: " + error[0]);
            return null;
        }
    }

    /**
     * The optimized-dex directory a DexClassLoader wants as its second argument.
     * Ignored from API 26 on, harmless before that.
     */
    private static String optimizedDir(Context context) {
        try {
            File dir = context.getDir("dex", Context.MODE_PRIVATE);
            //noinspection ResultOfMethodCallIgnored
            dir.mkdirs();
            return dir.getAbsolutePath();
        } catch (Throwable t) {
            return null;
        }
    }

    static void delete(File f) {
        if (f != null) {
            //noinspection ResultOfMethodCallIgnored
            f.delete();
        }
    }

    private static void readMeta(Class<?> type, Meta meta) {
        for (Annotation a : type.getAnnotations()) {
            if (!"org.vekendian.nexus.api.ModuleManifest".equals(a.annotationType().getName())) {
                continue;
            }
            try {
                meta.name = (String) a.annotationType().getMethod("name").invoke(a);
                meta.description = (String) a.annotationType().getMethod("description").invoke(a);
                meta.version = ((Integer) a.annotationType().getMethod("version").invoke(a)).intValue();
                meta.autostart = ((Boolean) a.annotationType().getMethod("autostart").invoke(a)).booleanValue();
            } catch (Throwable t) {
                Log.e(NexusHost.TAG, "annotation read failed: " + t);
            }
            return;
        }
    }

    /** Invokes an optional {@code onLoad(ModuleApi)} / {@code onUnload()}. */
    static void call(Object module, String name, Class<?>[] sig, Object[] args, String[] error) {
        if (module == null) {
            return;
        }
        try {
            Method m = module.getClass().getMethod(name, sig);
            m.invoke(module, args);
        } catch (NoSuchMethodException e) {
            // Optional by contract: a module that does not declare it is fine.
        } catch (Throwable t) {
            error[0] = name + "() failed: " + describe(t);
            Log.e(NexusHost.TAG, error[0]);
        }
    }

    static String describe(Throwable t) {
        if (t == null) {
            return "?";
        }
        String msg = t.getMessage();
        return msg == null || msg.length() == 0 ? t.getClass().getSimpleName()
                                                : msg;
    }

    static String join(String[] parts) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(parts[i]);
        }
        return sb.toString();
    }

    /**
     * Closes a DexClassLoader when the platform says it can be closed.
     *
     * <p>BaseDexClassLoader only implements Closeable from API 26, so this is an
     * instanceof check rather than a typed close: the classes already loaded
     * stay usable either way, and leaking the loader is harmless until the
     * process dies.
     */
    static void closeQuietly(Object c) {
        if (!(c instanceof java.io.Closeable)) {
            return;
        }
        try {
            ((java.io.Closeable) c).close();
        } catch (Throwable ignored) {
            // nothing useful to do
        }
    }

    static void close(java.io.Closeable c) {
        if (c == null) {
            return;
        }
        try {
            c.close();
        } catch (IOException ignored) {
            // nothing useful to do
        }
    }
}