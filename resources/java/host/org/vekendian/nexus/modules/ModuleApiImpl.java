package org.vekendian.nexus.modules;

import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.vekendian.nexus.api.ModuleApi;
import org.vekendian.nexus.api.NexusExecutor;

/**
 * The ModuleApi handed to the Module Registry, which passes the same object on to
 * every module it loads.
 *
 * <p>One instance for the process, created by {@link NexusHost}. It deliberately
 * does not cache the Activity in a strong reference: NexusHost holds the
 * activity it was last resumed with, and an Activity that has been destroyed
 * must not be kept alive by a module's reference to the API.
 */
final class ModuleApiImpl implements ModuleApi {

    @Override
    public Context context() {
        return NexusHost.app();
    }

    @Override
    public Activity activity() {
        return NexusHost.activity();
    }

    @Override
    public void log(String message) {
        Log.e(NexusHost.TAG, message == null ? "(null)" : message);
    }

    @Override
    public void toast(final String message) {
        if (message == null) {
            return;
        }
        // The Nexus toast, so a module's message looks like the rest of the
        // app and, more importantly, is drawn above GameGuardian's overlay
        // windows instead of behind them.
        NexusToast.show(context(), message, NexusToast.NEUTRAL);
    }

    @Override
    public String modulesDir() {
        return NexusHost.modulesDir();
    }

    @Override
    public void modulesChanged() {
        NexusHost.rerender();
    }

    @Override
    public String appVersion() {
        Context c = context();
        if (c == null) {
            return "?";
        }
        try {
            PackageManager pm = c.getPackageManager();
            PackageInfo info = pm.getPackageInfo(c.getPackageName(), 0);
            return info.versionName == null ? "?" : info.versionName;
        } catch (Throwable t) {
            return "?";
        }
    }

    @Override
    public ClassLoader getModuleClassLoader(String moduleId) {
        NexusExecutor executor = NexusHost.executor();
        if (executor != null) {
            return executor.loadLibrary(moduleId);
        }
        return null;
    }

    @Override
    public Object loadModule(String moduleId) {
        NexusExecutor executor = NexusHost.executor();
        if (executor != null) {
            return executor.loadModule(moduleId);
        }
        return null;
    }
}