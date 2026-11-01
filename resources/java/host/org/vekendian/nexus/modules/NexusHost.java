package org.vekendian.nexus.modules;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.view.ContextThemeWrapper;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.vekendian.nexus.api.ModuleApi;
import org.vekendian.nexus.api.ModuleInfo;
import org.vekendian.nexus.api.NexusExecutor;

import java.io.File;
import java.io.InputStream;
import java.util.List;
import java.util.Locale;

/**
 * The module system: everything the MODULES tab needs, with GameGuardian's
 * {@code android.ext.r} reduced to four one-line delegates.
 *
 * <p>Layering, which is the point of the module system:
 *
 * <pre>
 *   NexusHost  (this file, in the APK)      loads exactly one module:
 *       res/raw/ydw_nexus_dexexec  -->  Module Registry
 *   Module Registry (its own .dex)       loads the user's modules:
 *       files/modules/<name>.lua  -->  loadstring
 *       files/modules/<name>.jar  -->  DexClassLoader + LuaJava
 * </pre>
 *
 * <p>The host knows how to load <em>one</em> module and how to draw cards. The
 * registry knows how to import, run, stop and delete modules and reports state
 * through {@link ModuleInfo}. Neither reaches into the other's classes except
 * through the API jar, so the registry can be replaced without touching this
 * file, and a broken registry can only break the MODULES tab.
 *
 * <p>All static, all living for the process. Modules stop when the user powers
 * the interface off, not when the activity goes away: a module that draws an
 * overlay is expected to outlive the front page.
 */
public final class NexusHost {

    public static final String TAG = "NexusMod";

    /**
     * The SAF proxy, named rather than referenced.
     *
     * <p>ModulePicker is hand-written smali in this same APK, so a class literal
     * would compile -- but naming it keeps the compile-time dependency out of
     * the engine and out of build/module-api.jar, and it is how the picker was
     * launched before the engine existed.
     */
    private static final String PICKER_CLASS = "org.vekendian.nexus.ModulePicker";

    /**
     * What the picker may pick. Lua, JAR and DEX: the registry rejects other types.
     * DocumentsUI narrows to this list once EXTRA_MIME_TYPES is present.
     */
    private static final String[] PICK_MIME = {
            "application/octet-stream",
            "application/vnd.android.dex-archive",
            "application/java-archive",
            "text/plain",
    };

    /** Module directory under filesDir(). Owned by the registry. */
    private static final String MODULES_DIR = "modules";

    /** Indices into the id array render() receives. */
    private static final int I_LIST = 0, I_EMPTY = 1, I_CARD = 2, I_TITLE = 3,
            I_META = 4, I_DESC = 5, I_REMOVE = 6, I_EXEC = 7, I_LOADED = 8,
            I_IDLE = 9, I_RUN = 10, I_FIN = 11, I_STOP = 12, I_ERROR = 13,
            I_REMOVE_TITLE = 14, I_REMOVE_MSG = 15;

    private static ModuleApiImpl api;
    private static Context app;
    private static Activity activity;
    private static int rawId;
    private static volatile Uri pending;
    private static NexusExecutor executor;
    private static Object module;
    private static String failure;
    private static String moduleName = "";
    private static int moduleVersion;
    private static int[] ids;

    private NexusHost() {
    }

    // ---------------------------------------------------- smali entry points ---

    /**
     * Launch the SAF picker behind the proxy activity.
     *
     * <p>Plain startActivity, not startActivityForResult: the host is
     * singleInstance and can never receive a result. The proxy parks the chosen
     * Uri via {@link #park}; the host drains it in {@link #boot}.
     */
    public static void pick(Activity host) {
        if (host == null) {
            return;
        }
        try {
            Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("*/*");
            i.putExtra(Intent.EXTRA_MIME_TYPES, PICK_MIME);
            i.setClassName(host, PICKER_CLASS);
            host.startActivity(i);
        } catch (Throwable t) {
            log("picker failed: " + ModuleLoader.describe(t));
        }
    }

    /**
     * Called by ModulePicker while it still holds the picker's result.
     *
     * <p>The read grant that comes back from ACTION_OPEN_DOCUMENT is temporary
     * and is released when the activity that received the result finishes. The
     * copy happens later, on the host's next resume, so the persistable grant
     * has to be taken HERE -- before ModulePicker calls finish() -- or the
     * deferred copy fails with SecurityException and the import is silently
     * rejected. A provider that does not offer persistable grants still gets a
     * chance: the copy may happen before the temporary grant is reclaimed.
     */
    public static void parkFromActivity(Activity act, Uri uri) {
        if (uri != null && act != null) {
            try {
                act.getContentResolver().takePersistableUriPermission(
                        uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            } catch (Throwable t) {
                log("persistable grant refused at pick: " + ModuleLoader.describe(t));
            }
        }
        park(uri);
    }

    /** Called by ModulePicker once the user has chosen a document. */
    public static void park(Uri uri) {
        pending = uri;
        if (uri != null) {
            log("parked " + uri);
        }
    }

    /**
     * Per-resume: note the raw id, drain any parked Uri into the executor, then
     * start autostart modules. Idempotent -- the module load is attempted once
     * per process however often Nexus resumes.
     */
    public static void boot(Activity host, int rawResId) {
        if (host == null) {
            return;
        }
        if (app == null) {
            app = host.getApplicationContext();
            api = new ModuleApiImpl();
        }
        activity = host;
        rawId = rawResId;
        ensureExecutor();

        Uri uri = pending;
        if (uri != null) {
            // Cleared before the import so a re-entrant resume cannot import the
            // same document twice.
            pending = null;
            importUri(uri);
        }
        powerOn();
    }

    /**
     * Draws the tab.
     *
     * <p>The ids arrive as arguments rather than being looked up by name, so they
     * stay pinned in nexus_ids.json and the generated smali stays byte-stable.
     * They are cached, because a card's remove control has to repaint without
     * going back through the smali.
     */
    public static void render(Activity host,
                              int listId, int emptyId, int cardLayoutId,
                              int titleId, int metaId, int descId, int removeId,
                              int strExecutor, int strLoaded, int strIdle,
                              int strRunning, int strFinished, int strStopped,
                              int strError, int strRemoveTitle,
                              int strRemoveMsg) {
        if (host == null) {
            return;
        }
        activity = host;
        ids = new int[] { listId, emptyId, cardLayoutId, titleId, metaId, descId,
                removeId, strExecutor, strLoaded, strIdle, strRunning,
                strFinished, strStopped, strError, strRemoveTitle,
                strRemoveMsg };
        draw(host, ids);
    }

    /** Interface powered on (or resumed): start autostart modules. */
    public static void powerOn() {
        if (executor == null) {
            return;
        }
        try {
            executor.runAll();
        } catch (Throwable t) {
            log("runAll failed: " + ModuleLoader.describe(t));
        }
    }

    /**
     * Say something.
     *
     * <p>Not a stock Toast: a toast is drawn behind GameGuardian's overlay
     * windows, so the feedback after a module action would have been
     * invisible exactly when it mattered. NexusToast puts the same pill in
     * an overlay of its own.
     */
    private static void toast(Context context, String text) {
        NexusToast.show(context, text, NexusToast.NEUTRAL);
    }

    /** Interface powered off: stop every running script. */
    public static void powerOff() {
        if (executor == null) {
            return;
        }
        try {
            executor.stopAll();
        } catch (Throwable t) {
            log("stopAll failed: " + ModuleLoader.describe(t));
        }
    }

    // ------------------------------------------------------------- plumbing ---

    static Context app() {
        return app;
    }

    static Activity activity() {
        return activity;
    }

    /**
     * The loaded Module Registry, or null when the engine never started. The Lua
     * bridge and the permission policy both route through this: a script that
     * calls {@code nexus.modules.*} before Nexus boots gets
     * "module system is not running" instead of a prompt.
     */
    public static NexusExecutor executor() {
        return executor;
    }

    /**
     * The floating Settings Permissions screen.
     *
     * <p>Ids arrive as arguments ({@code r} = title, allow, ask, allow-all,
     * ask-all, reset, reset-done, close, then the three capability labels) for
     * the same reason {@link #render} takes them: this class is compiled before
     * the resource table exists. Each row has Allow and Ask buttons rather than
     * a checkbox, so the current state is always visible and changing it is one
     * tap.
     */
    public static void permissions(final Context host, final int[] r) {
        if (host == null || r == null || r.length < 11) {
            return;
        }
        final Context ui = dialogContext();
        if (ui == null) {
            log("permissions dialog needs a running Nexus host");
            return;
        }
        try {
            LuaBridge.migrateBroadGrants();
            final String[] caps = LuaBridge.capabilities();
            final Button[] allow = new Button[caps.length];
            final Button[] ask = new Button[caps.length];
            final AlertDialog[] dialog = new AlertDialog[1];

            LinearLayout root = new LinearLayout(ui);
            root.setOrientation(LinearLayout.VERTICAL);
            root.setPadding(dp(ui, 20), dp(ui, 8), dp(ui, 20), dp(ui, 4));

            // What this screen actually edits. Without it the rows read as
            // per-script permissions, which they are not.
            TextView scope = new TextView(ui);
            scope.setText(text(ui, "nexus_str_perm_default_note", ""));
            scope.setTextSize(12);
            scope.setTextColor(colorValue(ui, "nexus_orange_dim", 0xffffb366));
            scope.setPadding(0, 0, 0, dp(ui, 4));
            root.addView(scope);

            for (int i = 0; i < caps.length; i++) {
                final String cap = caps[i];
                LinearLayout row = new LinearLayout(ui);
                row.setOrientation(LinearLayout.HORIZONTAL);
                row.setGravity(Gravity.CENTER_VERTICAL);
                row.setPadding(0, dp(ui, 6), 0, dp(ui, 6));

                // Label, and -- when a script has answered for itself -- the
                // line that says so.
                LinearLayout labelBox = new LinearLayout(ui);
                labelBox.setOrientation(LinearLayout.VERTICAL);

                TextView label = new TextView(ui);
                if (i + 8 < r.length) {
                    label.setText(r[i + 8]);
                } else {
                    label.setText(cap);
                }
                label.setTextSize(15);
                labelBox.addView(label);

                if (LuaBridge.scriptOverride(cap)) {
                    TextView override = new TextView(ui);
                    override.setText(text(ui, "nexus_str_perm_script_override", ""));
                    override.setTextSize(12);
                    override.setTextColor(colorValue(ui, "nexus_text2", 0xffa8a8b0));
                    labelBox.addView(override);
                }
                labelBox.setLayoutParams(new LinearLayout.LayoutParams(
                        0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
                row.addView(labelBox);

                final Button a = permissionButton(ui, r[1]);
                final Button b = permissionButton(ui, r[2]);
                allow[i] = a;
                ask[i] = b;
                a.setOnClickListener(new View.OnClickListener() {
                    public void onClick(View v) {
                        LuaBridge.setGlobal(cap, true);
                        syncPermissionButtons(ui, caps, allow, ask);
                    }
                });
                b.setOnClickListener(new View.OnClickListener() {
                    public void onClick(View v) {
                        LuaBridge.setGlobal(cap, false);
                        syncPermissionButtons(ui, caps, allow, ask);
                    }
                });
                row.addView(a);
                row.addView(b);
                root.addView(row);
            }

            LinearLayout footer1 = new LinearLayout(ui);
            footer1.setOrientation(LinearLayout.HORIZONTAL);
            footer1.setPadding(0, dp(ui, 10), 0, 0);
            Button all = permissionButton(ui, r[3], false);
            all.setLayoutParams(footerParams(ui));
            all.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    for (String cap : caps) {
                        LuaBridge.setGlobal(cap, true);
                    }
                    syncPermissionButtons(ui, caps, allow, ask);
                }
            });
            Button none = permissionButton(ui, r[4], false);
            none.setLayoutParams(footerParams(ui));
            none.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    for (String cap : caps) {
                        LuaBridge.setGlobal(cap, false);
                    }
                    syncPermissionButtons(ui, caps, allow, ask);
                }
            });
            footer1.addView(all);
            footer1.addView(none);
            root.addView(footer1);

            LinearLayout footer2 = new LinearLayout(ui);
            footer2.setOrientation(LinearLayout.HORIZONTAL);
            footer2.setPadding(0, dp(ui, 6), 0, 0);
            Button forget = permissionButton(ui, r[5], false);
            forget.setLayoutParams(footerParams(ui));
            forget.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    LuaBridge.clearRemembered();
                    NexusToast.show(ui, ui.getString(r[6]), NexusToast.NEUTRAL);
                }
            });
            Button close = permissionButton(ui, r[7], false);
            close.setLayoutParams(footerParams(ui));
            close.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    if (dialog[0] != null) {
                        dialog[0].dismiss();
                    }
                }
            });
            footer2.addView(forget);
            footer2.addView(close);
            root.addView(footer2);

            dialog[0] = new AlertDialog.Builder(ui)
                    .setTitle(r[0])
                    .setView(root)
                    .setCancelable(true)
                    .create();
            syncPermissionButtons(ui, caps, allow, ask);
            showDialog(ui, dialog[0]);
        } catch (Throwable t) {
            log("permissions dialog failed: " + ModuleLoader.describe(t));
        }
    }

    /**
     * A NexusDialog-themed context based on the application, not on whichever
     * Context happens to own the clicked row. A Service/row context produces a
     * dialog with GG's old theme; the application context also has no Activity
     * window token, which is what lets the dialog window be promoted above the
     * floating interface.
     */
    private static Context dialogContext() {
        Context base = app != null ? app : activity;
        return base == null ? null : themedContext(base);
    }

    private static Context themedContext(Context base) {
        int theme = resourceId(base, "NexusDialog", "style");
        if (theme == 0) {
            theme = android.R.style.Theme_Material_Dialog_Alert;
        }
        return new ContextThemeWrapper(base, theme);
    }

    /**
     * The Lua prompt builds Android's AlertDialog directly, so it asks for the
     * same themed builder here. Null means Nexus has not booted yet; the prompt
     * declines rather than showing a window with the wrong theme.
     */
    public static AlertDialog.Builder dialogBuilder() {
        Context ui = dialogContext();
        return ui == null ? null : new AlertDialog.Builder(ui);
    }

    /**
     * GameGuardian's single builder factory ({@code android.ext.f.c}) delegates
     * here, so every GG dialog gets NexusDialog instead of the framework's
     * default theme. Wrapping the caller's Context, rather than replacing it
     * with the application Context, preserves an Activity window token for the
     * dialogs that are shown inside an Activity.
     */
    public static AlertDialog.Builder dialogBuilder(Context base) {
        return base == null ? null : new AlertDialog.Builder(themedContext(base));
    }

    /**
     * Show above GG's floating interface.
     *
     * <p>An ordinary Activity dialog is a sub-window below the overlay panel.
     * The application-context dialog is given the same overlay type GG uses
     * (TYPE_APPLICATION_OVERLAY on API 26+, TYPE_PHONE below it), so it is a
     * separate top-level window created after the panel and therefore lands
     * above it. The Nexus surface and filled primary button mirror GG's dialog
     * funnel (android.ext.f.t) because host-built dialogs do not pass through
     * that funnel.
     */
    private static void showDialog(Context ui, AlertDialog dialog) {
        if (ui == null || dialog == null) {
            return;
        }
        Window window = dialog.getWindow();
        if (window != null) {
            int surface = resourceId(ui, "nexus_bg_dialog", "drawable");
            if (surface != 0) {
                window.setBackgroundDrawableResource(surface);
            }
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    window.setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY);
                } else {
                    window.setType(WindowManager.LayoutParams.TYPE_PHONE);
                }
            } catch (Throwable t) {
                log("dialog overlay type failed: " + ModuleLoader.describe(t));
            }
        }
        try {
            dialog.show();
        } catch (Throwable t) {
            log("dialog show failed: " + ModuleLoader.describe(t));
            return;
        }
        Button positive = dialog.getButton(AlertDialog.BUTTON_POSITIVE);
        Button negative = dialog.getButton(AlertDialog.BUTTON_NEGATIVE);
        Button neutral = dialog.getButton(AlertDialog.BUTTON_NEUTRAL);
        int margin = dp(ui, 12);
        if (positive != null) {
            int primary = resourceId(ui, "nexus_bg_primary", "drawable");
            if (primary != 0) {
                positive.setBackgroundResource(primary);
            }
            positive.setTextColor(0xff1a1a1c);
            positive.setPadding(margin, 0, margin, 0);
        }
        if (negative != null) {
            negative.setTextColor(colorValue(ui, "nexus_text2", 0xffa8a8b0));
            negative.setPadding(margin, 0, margin, 0);
        }
        if (neutral != null) {
            neutral.setTextColor(colorValue(ui, "nexus_text2", 0xffa8a8b0));
            neutral.setPadding(margin, 0, margin, 0);
        }
    }

    static int resourceId(Context context, String name, String kind) {
        try {
            return context.getResources().getIdentifier(
                    name, kind, context.getPackageName());
        } catch (Throwable t) {
            return 0;
        }
    }

    /**
     * A string resource by name.
     *
     * <p>The host is compiled before the resource table exists, so a string it
     * needs at runtime is looked up by name. The fallback is what the user
     * sees if the resource is missing, which is why it is the same wording.
     */
    private static String text(Context context, String name, String fallback) {
        int id = resourceId(context, name, "string");
        if (id == 0) {
            return fallback;
        }
        try {
            return context.getString(id);
        } catch (Throwable t) {
            return fallback;
        }
    }

    /** A colour resource by name, or 0 when it is missing. */
    private static int color(Context context, String name) {
        return resourceId(context, name, "color");
    }

    /**
     * A colour by resource name, resolved to the ARGB value setTextColor wants.
     *
     * <p>{@link #color} returns a resource ID, not a colour. Passing that ID
     * to setTextColor(int) reads 0x7f06xxxx as ARGB: a half-transparent navy,
     * which is the dark blue the note and the footer labels used to wear.
     */
    @SuppressWarnings("deprecation")
    private static int colorValue(Context context, String name, int fallback) {
        int id = color(context, name);
        if (id == 0) {
            return fallback;
        }
        try {
            return context.getResources().getColor(id);
        } catch (Throwable t) {
            return fallback;
        }
    }

    /**
     * A button in the permissions dialog.
     *
     * <p>A choice button (Allow / Ask) wears nexus_bg_choice and carries a
     * check when its side is the one in effect. An action button (Allow all,
     * Forget script choices, Close) wears nexus_bg_button and never the check.
     * Orange fill on both: the selected choice and the footer actions, with
     * white labels.
     *
     * <p>The width is fixed so the pair stays even when the check appears on
     * one side only.
     */
    private static Button permissionButton(Context host, int text) {
        return permissionButton(host, text, true);
    }

    private static Button permissionButton(Context host, int text, boolean choice) {
        Button b = new Button(host);
        b.setText(text);
        b.setAllCaps(false);
        b.setGravity(Gravity.CENTER);
        b.setMinWidth(dp(host, 88));
        b.setMinimumWidth(dp(host, 88));
        b.setPadding(dp(host, 10), 0, dp(host, 10), 0);
        int bg = resourceId(host, choice ? "nexus_bg_choice" : "nexus_bg_button",
                            "drawable");
        if (bg != 0) {
            b.setBackgroundResource(bg);
        }
        // The theme's android:buttonStyle paints this same orange pill on top
        // of our explicit one; clearing the tint list has kept the explicit
        // background visible since the tint-carrying styles were removed.
        b.setBackgroundTintList(null);
        if (choice) {
            int colors = resourceId(host, "nexus_choice_text", "color");
            if (colors != 0) {
                b.setTextColor(b.getResources().getColorStateList(colors));
            }
        } else {
            b.setTextColor(colorValue(host, "nexus_text", 0xffffffff));
        }
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(dp(host, 6), 0, 0, 0);
        b.setLayoutParams(lp);
        return b;
    }

    /**
     * Paint the pair to match the stored state.
     *
     * <p>Three channels say the same thing: the fill (orange on the side in
     * effect), the check glyph, and the label colour. The side in effect is
     * also the side that cannot be clicked, which used to be the only cue --
     * and it was invisible, because nothing in the two selectors described
     * the disabled state.
     */
    private static void syncPermissionButtons(Context ui, String[] caps,
                                              Button[] allow, Button[] ask) {
        int check = resourceId(ui, "nexus_ic_check", "drawable");
        for (int i = 0; i < caps.length; i++) {
            boolean on = LuaBridge.global(caps[i]);
            if (allow[i] != null) {
                allow[i].setSelected(on);
                allow[i].setEnabled(true);
                markChosen(allow[i], on, check);
            }
            if (ask[i] != null) {
                ask[i].setSelected(!on);
                ask[i].setEnabled(true);
                markChosen(ask[i], !on, check);
            }
        }
    }

    private static void markChosen(Button b, boolean chosen, int check) {
        if (chosen && check != 0) {
            b.setCompoundDrawablesRelativeWithIntrinsicBounds(0, 0, check, 0);
        } else {
            b.setCompoundDrawablesRelativeWithIntrinsicBounds(0, 0, 0, 0);
        }
    }

    /** Equal-width footer button with a gap on each side. */
    private static LinearLayout.LayoutParams footerParams(Context host) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        lp.setMargins(dp(host, 4), 0, dp(host, 4), 0);
        return lp;
    }

    private static int dp(Context context, int value) {
        return (int) (value * context.getResources().getDisplayMetrics().density + 0.5f);
    }

    static String modulesDir() {
        return new File(app.getFilesDir(), MODULES_DIR).getAbsolutePath();
    }

    static void log(String message) {
        android.util.Log.e(TAG, message);
    }

    private static void importUri(final Uri uri) {
        if (executor == null) {
            importFailed(failure == null ? "executor not loaded" : failure);
            return;
        }
        // Copying and class-loading a dex is disk I/O; doing it in onPostResume
        // freezes the interface for as long as the provider takes to read.
        Thread t = new Thread(new Runnable() {
            public void run() {
                importUriNow(uri);
            }
        }, "NexusModules:import");
        t.start();
    }

    private static void importUriNow(Uri uri) {
        String unreadable = probeReadable(uri);
        if (unreadable != null) {
            importFailed(unreadable);
            return;
        }
        try {
            String id = executor.add(app, uri);
            log("import -> " + (id == null ? "rejected" : id));
            if (id == null) {
                importFailed("the picked file is not a loadable module (.lua or .jar)");
                return;
            }
            rerender();
        } catch (Throwable t) {
            importFailed(ModuleLoader.describe(t));
        }
    }

    /** The copy is deferred to the next resume; proves the grant survived. */
    private static String probeReadable(Uri uri) {
        InputStream in = null;
        try {
            in = app.getContentResolver().openInputStream(uri);
            if (in == null) {
                return "the picked file cannot be opened";
            }
            if (in.read() < 0) {
                return "the picked file is empty";
            }
            return null;
        } catch (Throwable t) {
            return ModuleLoader.describe(t);
        } finally {
            if (in != null) {
                try {
                    in.close();
                } catch (Throwable ignored) {
                    // nothing useful to do
                }
            }
        }
    }

    private static void importFailed(final String why) {
        log("import failed: " + why);
        final Activity a = activity;
        if (a == null || app == null) {
            return;
        }
        a.runOnUiThread(new Runnable() {
            public void run() {
                NexusToast.show(app, "Module not added: " + why, NexusToast.ERROR);
            }
        });
    }

    /**
     * Loads the Module Registry asset. Once per process, and a failure is kept
     * rather than retried: the asset either loads or it does not, and retrying
     * on every resume would re-extract and re-verify a broken dex forever. The
     * reason is shown on the executor's card instead.
     */
    private static void ensureExecutor() {
        if (executor != null || failure != null) {
            return;
        }
        if (app == null || rawId == 0) {
            return;
        }
        File dex = ModuleLoader.extract(app, rawId);
        if (dex == null) {
            failure = "executor asset unavailable";
            return;
        }
        ModuleLoader.Meta meta = new ModuleLoader.Meta();
        String[] err = new String[1];
        Object m = ModuleLoader.load(app, NexusHost.class.getClassLoader(), dex, meta, err);
        if (m == null) {
            failure = err[0];
            return;
        }
        if (!(m instanceof NexusExecutor)) {
            failure = "entry class does not implement NexusExecutor";
            return;
        }
        module = m;
        executor = (NexusExecutor) m;
        moduleName = meta.name.length() == 0 ? "Nexus module" : meta.name;
        moduleVersion = meta.version;
        ModuleLoader.call(m, "onLoad", new Class<?>[] { ModuleApi.class },
                new Object[] { api }, err);
        if (err[0] != null) {
            failure = err[0];                  // registered, but its init threw
        }
        log("Module Registry loaded: " + moduleName + " v" + moduleVersion);
    }

    private static void draw(Activity host, int[] r) {
        View list = host.findViewById(r[I_LIST]);
        if (!(list instanceof ViewGroup)) {
            return;
        }
        ViewGroup parent = (ViewGroup) list;
        parent.removeAllViews();
        LayoutInflater inflater = LayoutInflater.from(host);

        // The built-in registry is infrastructure, not something the user
        // installed, so it has no card: the tab lists user modules only.
        int count = 0;
        List<ModuleInfo> modules = null;
        if (executor != null) {
            try {
                modules = executor.modules();
            } catch (Throwable t) {
                log("modules() failed: " + ModuleLoader.describe(t));
            }
        }
        if (modules != null) {
            for (ModuleInfo s : modules) {
                count++;
                ModuleCards.bind(inflater, parent, r, s.name(),
                        moduleMeta(host, s), moduleDesc(host, r, s),
                        statusColor(host, s), s);
            }
        }
        // "No modules" must mean "you have none", not "the loader failed": a
        // boot failure has no card of its own, so with nothing else to show the
        // empty state carries the reason instead of a misleading blank tab.
        View empty = host.findViewById(r[I_EMPTY]);
        if (empty != null) {
            if (count == 0 && failure != null && empty instanceof TextView) {
                ((TextView) empty).setText(failure);
            }
            empty.setVisibility(count == 0 ? View.VISIBLE : View.GONE);
        }
    }

    /**
     * The path relative to filesDir(), plus the size. Never an absolute path.
     *
     * <p>Also the autostart flag, because "Start autostart modules" is
     * otherwise a promise the user cannot check: a module that opted out
     * would silently ignore it.
     */
    private static String moduleMeta(Context host, ModuleInfo s) {
        String path = s.path() == null ? "" : s.path();
        String dir = modulesDir();
        String rel = path;
        if (rel.startsWith(dir)) {
            rel = rel.substring(dir.length());
        }
        while (rel.startsWith("/")) {
            rel = rel.substring(1);
        }
        if (rel.length() == 0) {
            rel = new File(path).getName();
        }
        String meta = rel + String.format(Locale.US, " · %.1f KB", s.size() / 1024.0);
        if (s.autostart()) {
            meta = meta + " · " + text(host, "nexus_str_extension_autostart", "autostart");
        }
        // Type badge. A .dex is not a .jar: both load classes, but only one of
        // them is an archive, and the card used to call every dex a JAR.
        if (s.type() == ModuleInfo.Type.JAR) {
            meta = meta + " · " + text(host, "nexus_str_extension_jar", "JAR Module");
        } else if (s.type() == ModuleInfo.Type.DEX) {
            meta = meta + " · " + text(host, "nexus_str_extension_dex", "DEX Module");
        }
        return meta;
    }

    /**
     * The status line's colour.
     *
     * <p>Every state used to be the same grey, so a running module and a
     * failed one looked identical. The tokens for this already existed and
     * nothing used them.
     */
    static int statusColor(Context host, ModuleInfo s) {
        // JAR modules show as loaded (green) since they don't run
        if ((s.type() == ModuleInfo.Type.JAR || s.type() == ModuleInfo.Type.DEX)) {
            return color(host, "nexus_ok");
        }
        switch (s.state()) {
            case ModuleInfo.STATE_RUNNING:
                return color(host, "nexus_ok");
            case ModuleInfo.STATE_ERROR:
                return color(host, "nexus_bad");
            case ModuleInfo.STATE_FINISHED:
                return color(host, "nexus_text");
            default:
                return color(host, "nexus_text2");
        }
    }

    private static String moduleDesc(Activity host, int[] r, ModuleInfo s) {
        // JAR modules always show "Loaded"
        if ((s.type() == ModuleInfo.Type.JAR || s.type() == ModuleInfo.Type.DEX)) {
            return host.getString(r[I_LOADED]);
        }
        switch (s.state()) {
            case ModuleInfo.STATE_RUNNING:
                return host.getString(r[I_RUN]);
            case ModuleInfo.STATE_FINISHED:
                return host.getString(r[I_FIN]);
            case ModuleInfo.STATE_STOPPED:
                return host.getString(r[I_STOP]);
            case ModuleInfo.STATE_ERROR:
                return host.getString(r[I_ERROR]).replace("%s",
                        s.message() == null ? "?" : s.message());
            case ModuleInfo.STATE_IDLE:
            default:
                return s.description() == null || s.description().length() == 0
                        ? host.getString(r[I_IDLE]) : s.description();
        }
    }

    /** Drop a module, then repaint. Called from a card's remove control. */
    private static void removeModule(ModuleInfo s) {
        if (executor == null || s == null) {
            return;
        }
        try {
            log("remove " + s.path() + " -> " + executor.remove(s.path()));
        } catch (Throwable t) {
            log("remove failed: " + ModuleLoader.describe(t));
        }
        rerender();
    }

    /**
     * Repaint after an action a card started.
     *
     * <p>Posted rather than called inline: the executor's own work may have run
     * off the main thread, and findViewById/setText need it back.
     */
    static void rerender() {
        final Activity a = activity;
        final int[] r = ids;
        if (a == null || r == null) {
            return;
        }
        a.runOnUiThread(new Runnable() {
            public void run() {
                activity = a;
                draw(a, r);
            }
        });
    }

    /** Runs the card's action, then repaints. */
    static void onRemoveClicked(ModuleInfo s) {
        if (s == null) {
            return;
        }
        final Activity a = activity;
        final int[] r = ids;
        if (a == null || r == null) {
            removeModule(s);
            return;
        }
        final Context ui = dialogContext();
        if (ui == null) {
            removeModule(s);
            return;
        }
        AlertDialog dialog = new AlertDialog.Builder(ui)
                .setTitle(r[I_REMOVE_TITLE])
                .setMessage(ui.getString(r[I_REMOVE_MSG],
                        s.name() == null ? s.path() : s.name()))
                .setPositiveButton(android.R.string.ok,
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                removeModule(s);
                            }
                        })
                .setNegativeButton(android.R.string.cancel, null)
                .create();
        showDialog(ui, dialog);
    }
}