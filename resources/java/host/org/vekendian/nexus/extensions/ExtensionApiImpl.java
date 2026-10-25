package org.vekendian.nexus.extensions;

import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.vekendian.nexus.api.ExtensionApi;
import org.vekendian.nexus.api.NexusExecutor;

/**
 * The ExtensionApi handed to the Extension Registry, which passes the same object on to
 * every extension it loads.
 *
 * <p>One instance for the process, created by {@link NexusHost}. It deliberately
 * does not cache the Activity in a strong reference: NexusHost holds the
 * activity it was last resumed with, and an Activity that has been destroyed
 * must not be kept alive by a extension's reference to the API.
 */
final class ExtensionApiImpl implements ExtensionApi {

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
        // The Nexus toast, so an extension's message looks like the rest of the
        // app and, more importantly, is drawn above GameGuardian's overlay
        // windows instead of behind them.
        NexusToast.show(context(), message, NexusToast.NEUTRAL);
    }

    @Override
    public String extensionsDir() {
        return NexusHost.extensionsDir();
    }

    @Override
    public void extensionsChanged() {
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
    public ClassLoader getExtensionClassLoader(String extensionId) {
        NexusExecutor executor = NexusHost.executor();
        if (executor != null) {
            return executor.loadLibrary(extensionId);
        }
        return null;
    }

    @Override
    public Object loadExtension(String extensionId) {
        NexusExecutor executor = NexusHost.executor();
        if (executor != null) {
            return executor.loadExtension(extensionId);
        }
        return null;
    }
}