package nexus;

import org.vekendian.nexus.api.ModuleInfo;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.lang.reflect.Method;

/**
 * Runs a .lua module on its own thread inside GameGuardian's LuaJ.
 *
 * <p>The engine dex links against android.jar only, so every piece of LuaJ --
 * the state, the libraries, even the chunk loader -- is reached reflectively,
 * and the member names below are GameGuardian 101.4's obfuscated ones: the same
 * names the tree's smali anchors pin. A GameGuardian update that reshuffles
 * them fails exactly the way it fails every other anchor, with an exception
 * whose message names the class, and build-engine.sh regenerates the dex from
 * this source.
 *
 * <p>The sequence mirrors GameGuardian's own source runner
 * ({@code android/ext/Script.F3}): a fresh Globals, the seven standard
 * libraries installed through LuaValue.t1, gg.* installed through Script.K3,
 * then Globals.O3 to load the file's chunk and call() to run it. On top of
 * that the environment gets the {@code nexus.*} table through NexusLua.install
 * -- the same entry point Script.call uses for every GG script -- with the
 * module's own path as the permission label, so prompts and permission rows
 * name the module whose script asked.
 *
 * <p>GameGuardian's own env setup ({@code Script.u3}) needs no mirroring beyond
 * what {@link #runChunk} does: the one required member is {@code g/h.M}, the
 * load-hook pass (compiler and closure-maker), without which every load throws
 * "No compiler." Exception decorations beyond that live on the record itself --
 * a throw from load or call lands in {@code failed()} and shows on the
 * module's card.
 */
final class LuaModuleLoader {

    private static final String TAG = "NexusMod";

    // GameGuardian 101.4 obfuscated members, used reflectively. Not mirrored
    // from F3 there: Globals.X stays true (the constructor default) so the
    // environment installs _G and setmetatable, which real Lua code uses.
    private static final String GLOBALS_CLASS = "luaj.Globals";
    private static final String LUAVALUE_CLASS = "luaj.LuaValue";
    private static final String GG_SCRIPT_CLASS = "android.ext.Script";
    private static final String LUA_INSTALL_LIB = "t1";
    private static final String GG_INSTALL = "K3";
    private static final String LUA_LOAD = "O3";
    private static final String NEXUS_INSTALL_CLASS = "org.vekendian.nexus.lua.NexusLua";
    private static final String GG_LOAD_HOOK_CLASS = "g.h";
    private static final String GG_LOAD_HOOK_INSTALL = "M";
    private static final String[] LUA_LIBS = {
            "luaj.lib.BaseLib", "luaj.lib.Bit32Lib", "luaj.lib.TableLib",
            "luaj.lib.StringLib", "luaj.lib.Utf8Lib", "luaj.lib.MathLib",
            "luaj.lib.OsLib",
    };

    private LuaModuleLoader() {
    }

    /**
     * Marks the record RUNNING and starts the chunk on a fresh thread.
     * Terminal state lands through host.finished/failed -- the same contract a
     * Java entry class had.
     */
    static void start(final ModuleRegistry host, final ModuleRecord rec) {
        rec.stopRequested = false;
        rec.state = ModuleInfo.STATE_RUNNING;
        rec.message = null;
        Thread t = new Thread(new Runnable() {
            public void run() {
                try {
                    runChunk(rec);
                } catch (Throwable e) {
                    host.failed(rec, e);
                    return;
                }
                host.finished(rec, rec.stopRequested);
            }
        }, "NexusModule:" + rec.name);
        rec.thread = t;
        t.start();
    }

    /**
     * Builds a Globals the way GameGuardian does, installs gg.* and the nexus
     * table, then runs the file's chunk to completion. A returning call is
     * success, not failure: that is how a Lua script ends.
     *
     * @throws Exception whatever GameGuardian's LuaJ raises on load or run; the
     *                   caller turns it into the record's error message
     */
    private static void runChunk(ModuleRecord rec) throws Exception {
        Class<?> globalsClass = Class.forName(GLOBALS_CLASS);
        Class<?> luaValueClass = Class.forName(LUAVALUE_CLASS);
        Object env = globalsClass.newInstance();
        // The load hooks. The g/h singleton IS the compiler hook, not a
        // decoration: it is the only writer of Globals.k0 (Globals$a) and
        // Globals.j0 (Globals$b) in the whole tree, and a Globals without them
        // throws "No compiler." the first time it loads source. GameGuardian's
        // own runners call g/h.M right after construction (Script.F3 and
        // Script.u3 both do), so the module runner does the same, before
        // any library install.
        Class.forName(GG_LOAD_HOOK_CLASS).getMethod(
                GG_LOAD_HOOK_INSTALL, globalsClass).invoke(null, env);

        Method installLib = luaValueClass.getMethod(LUA_INSTALL_LIB, luaValueClass);
        for (int i = 0; i < LUA_LIBS.length; i++) {
            installLib.invoke(env, Class.forName(LUA_LIBS[i]).newInstance());
        }
        // gg.* -- the same installer GameGuardian's own script thread goes
        // through.
        Method installGg = Class.forName(GG_SCRIPT_CLASS).getMethod(GG_INSTALL, globalsClass);
        installGg.invoke(null, env);
        // nexus.* -- the script namespace, labelled with the module's path
        // so the permission prompt names this module.
        Method installNexus = Class.forName(NEXUS_INSTALL_CLASS)
                .getMethod("install", String.class, luaValueClass);
        installNexus.invoke(null, rec.path, env);

        // loadstring. Mode "t" as in every GameGuardian load: the source is
        // text, never precompiled bytecode.
        Method load = globalsClass.getMethod(LUA_LOAD,
                InputStream.class, String.class, String.class, luaValueClass);
        Method call = luaValueClass.getMethod("call");
        InputStream in = new FileInputStream(new File(rec.path));
        try {
            Object chunk = load.invoke(env, in, rec.label(), "t", env);
            call.invoke(chunk);
        } finally {
            try {
                in.close();
            } catch (Throwable ignored) {
            }
        }
    }
}
