package org.vekendian.nexus.api;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Marks a method as exported to Lua via {@code nexus.modules.import}.
 *
 * <p>Only methods on the entry class (declared by {@link ModuleManifest#entry()})
 * are scanned. The method must be public and non-static (or static — both work).
 * The return type and parameter types determine the marshalling protocol:
 * <ul>
 *   <li>Parameters: {@code String}, {@code int}/{@code long}, {@code double}/{@code float},
 *       {@code boolean}, {@code String[]} (varargs, must be last)</li>
 *   <li>Returns: {@code void} (Lua gets {@code true}), {@code String}, {@code int}/{@code long}
 *       (Lua gets number), {@code double}/{@code float} (Lua gets number),
 *       {@code boolean} (Lua gets boolean)</li>
 * </ul>
 *
 * <p>Example:
 * <pre>
 *   @Export
 *   public void compress(String path, int level) { ... }
 *
 *   @Export
 *   public String read(String path) { ... }
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Export {
    /** Optional explicit Lua name. Defaults to the Java method name. */
    String value() default "";
}