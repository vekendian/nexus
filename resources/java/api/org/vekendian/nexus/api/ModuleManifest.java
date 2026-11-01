package org.vekendian.nexus.api;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Required metadata for a module entry class.
 *
 * <p>Kept to an annotation rather than an interface on purpose: the module
 * system's loader finds the entry class by name ({@code nexus.JarModuleLoader})
 * and reads this reflectively. The annotation is required for the registry
 * to identify itself.
 *
 * <p>{@code RUNTIME} retention is what makes the reflective read work at all --
 * {@code CLASS} would be dropped by dexing.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface ModuleManifest {

    /** Display name on the MODULES card. Falls back to the file's base name. */
    String name() default "";

    /** One line under the name. Falls back to the entry class name. */
    String description() default "";

    /** Module author's version number. Shown in the card's meta line. */
    int version() default 1;

    /**
     * Whether the Module Registry starts this module automatically when Nexus
     * resumes. An module without {@code run(ModuleApi)} is rejected before it can
     * appear as a card.
     */
    boolean autostart() default true;

    /**
     * Module type. Determines lifecycle, UI presence, and classloader strategy.
     *
     * <ul>
     *   <li>{@link ModuleType#LUA} (default): Lua script loaded via loadstring.
     *       Runs on Lua thread via LuaJava bridge.</li>
     *   <li>{@link ModuleType#JAR}: Java archive loaded via DexClassLoader.
     *       Classes exposed to Lua via LuaJava. No card, no run(), no auto-start.</li>
     * </ul>
     */
    ModuleType type() default ModuleType.LUA;

    /**
     * Module IDs (filenames without {@code .lua} or {@code .jar}) this module depends on.
     * Dependencies are loaded first.
     */
    String[] dependsOn() default {};

    /**
     * Override the entry class name. For JAR type: the main class to expose to Lua.
     */
    String entry() default "";
}