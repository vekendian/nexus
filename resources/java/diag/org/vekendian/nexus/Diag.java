package org.vekendian.nexus;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;

import java.util.zip.ZipFile;

/**
 * The init probe for the {@code MainService.G} crash.
 *
 * <p>The crash is a NullPointerException on {@code ListView.setAdapter} inside
 * {@code android.ext.MainService.Z0}. Z0 reads {@code MainService.G}, and G is
 * written in exactly two places, both inside {@code MainService.Z()}:
 *
 * <pre>
 *   4430  G = findViewById(0x7f05000a /* addr_list *&#47;)   on the inflated service_dialog
 *   4461  G = findViewById(0x7f050008 /* addr_item_type *&#47;) -- the catchall path
 * </pre>
 *
 * <p>Line 4461 is the failure path: {@code addr_item_type} is not in
 * {@code service_dialog.xml} at all, so it resolves to null and the later
 * {@code setAdapter} dereferences it. Reaching it means Z() took one of four
 * {@code .catchall} handlers that swallow the exception without logging, which
 * is why the logcat shows {@code Service onCreate} and then, ~120 ms later, the
 * NPE with nothing in between.
 *
 * <p>Every static check on the tree is already clean — MainService.smali is
 * byte-identical to stock in the built dex, public.xml has zero drift and zero
 * collisions, the compiled layout binds {@code @id/addr_list} at
 * {@code 0x7f05000a}, and {@code ZipFile} opens the built APK. So the question
 * is no longer "what does the tree say" but "what does the running process
 * return", and only the running process can answer that.
 *
 * <p>It runs from {@code nexusPowerApply()} on the main thread at
 * {@code onPostResume} — after MainActivity has inflated main.xml and before
 * the service starts — so it observes the state Z() will see a moment later.
 *
 * <p>Every step is wrapped. A probe that crashes takes the app down with it, and
 * the whole point is to find out what is already broken.
 */
public final class Diag {

    private static final String TAG = "NexusDiag";

    /** The layout Z() inflates at MainService.smali:4064. */
    private static final int L_SERVICE_DIALOG = 0x7f06001d;

    /** addr_list -- what G is bound from on the success path. */
    private static final int ID_ADDR_LIST = 0x7f05000a;

    /** addr_item_type -- what the catchall path binds instead, and it is absent
     *  from service_dialog, which is precisely why the crash lands on null. */
    private static final int ID_ADDR_ITEM_TYPE = 0x7f050008;

    private Diag() {
    }

    public static void probe() {
        try {
            log("===== MainService init probe =====");
            Context ctx = mainServiceContext();
            log("  MainService.context = " + describe(ctx));

            if (ctx == null) {
                log("  (null -- Z() could not even inflate; this is not the crash we know)");
                return;
            }

            LayoutInflater li = LayoutInflater.from(ctx);
            log("  LayoutInflater.from(ctx) = " + describe(li));
            log("  is GG's android.ext.a$d = " + (li != null
                    && li.getClass().getName().equals("android.ext.a$d")));

            Object window = ctx.getSystemService(Context.WINDOW_SERVICE);
            log("  getSystemService(\"window\") = " + describe(window)
                    + "   <- Z():4343 check-casts this to WindowManager;"
                    + " a CCE or NPE here is swallowed by :catchall_1");
            if (window != null && !(window instanceof android.view.WindowManager)) {
                log("  !!! not a WindowManager -- this IS the ClassCastException");
            }

            log("  getPackageResourcePath() = " + safePackagePath(ctx));
            log("  ZipFile entries = " + safeZipEntries(ctx));

            View root = inflate(ctx);
            log("  inflate(0x7f06001d service_dialog) = " + describe(root));
            if (root == null) {
                log("  !!! inflate returned null");
                return;
            }

            View addr = root.findViewById(ID_ADDR_LIST);
            log("  >>> findViewById(0x7f05000a addr_list) = " + describe(addr));
            if (addr == null) {
                log("  !!! THE ANSWER: the inflated layout does NOT contain addr_list."
                        + " G will be null and Z0 will NPE.");
            } else if (!(addr instanceof android.widget.ListView)) {
                log("  !!! addr_list is not a ListView: Z()'s check-cast throws");
            } else {
                log("  addr_list is a live ListView -- inflate is fine, so Z() lost G"
                        + " AFTER this point; look at the paths between 4430 and 5160");
            }

            log("  (for contrast) findViewById(0x7f050008 addr_item_type) on the same"
                    + " tree = " + describe(root.findViewById(ID_ADDR_ITEM_TYPE))
                    + "   <- this is what :catchall_1 binds, and it must be null");
            log("===== end probe =====");
        } catch (Throwable t) {
            log("  probe itself threw: " + describe(t) + ": " + t.getMessage());
        }
    }

    /** MainService.context, by reflection: GG's classes are not on javac's
     *  classpath, and this class must compile against the android jar alone. */
    private static Context mainServiceContext() {
        try {
            Class<?> ms = Class.forName("android.ext.MainService");
            return (Context) ms.getField("context").get(null);
        } catch (Throwable t) {
            log("  could not read MainService.context: " + describe(t)
                    + ": " + t.getMessage());
            return null;
        }
    }

    /** La/d.f -- GG's own inflater, not LayoutInflater.inflate, because Z() uses
     *  the former and the theme-retry wrapper in La/d is part of what we are
     *  testing. Falls back to the platform inflater if GG's class is absent. */
    private static View inflate(Context ctx) {
        try {
            return (View) Class
                    .forName("android.ext.a$d")
                    .getMethod("f", int.class, android.view.ViewGroup.class)
                    .invoke(null, L_SERVICE_DIALOG, null);
        } catch (Throwable t) {
            log("  La/d.f unavailable (" + describe(t) + "); using LayoutInflater.inflate");
            return LayoutInflater.from(ctx).inflate(L_SERVICE_DIALOG, null);
        }
    }

    private static String safePackagePath(Context ctx) {
        try {
            return ctx.getPackageResourcePath();
        } catch (Throwable t) {
            return "THREW " + describe(t) + ": " + t.getMessage();
        }
    }

    /** Z() opens a ZipFile on the package resource path at :try_start_0 and
     *  swallows any failure at :catchall_4, which skips the G assignment
     *  entirely. Entry count proves the open worked. */
    private static String safeZipEntries(Context ctx) {
        ZipFile z = null;
        try {
            z = new ZipFile(ctx.getPackageResourcePath());
            int n = 0;
            java.util.Enumeration<? extends java.util.zip.ZipEntry> e = z.entries();
            while (e.hasMoreElements()) {
                e.nextElement();
                n++;
            }
            return Integer.toString(n);
        } catch (Throwable t) {
            return "THREW " + describe(t) + ": " + t.getMessage();
        } finally {
            if (z != null) {
                try {
                    z.close();
                } catch (Throwable ignored) {
                    // nothing to do; the count is already logged
                }
            }
        }
    }

    private static String describe(Object o) {
        if (o == null) {
            return "null";
        }
        try {
            return o.getClass().getName();
        } catch (Throwable t) {
            return "<describe failed>";
        }
    }

    private static void log(String message) {
        Log.e(TAG, message);
    }
}