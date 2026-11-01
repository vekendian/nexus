package org.vekendian.nexus.api;

/**
 * Module type determines lifecycle, UI presence, and classloader strategy.
 */
public enum ModuleType {
    /** Lua script loaded via loadstring. Runs on Lua thread via LuaJava bridge. */
    LUA,

    /** Java archive loaded via DexClassLoader. Classes exposed to Lua via LuaJava. No card, no run(), no auto-start. */
    JAR,

    /** Raw Dalvik bytecode loaded via DexClassLoader. Same library model as JAR. */
    DEX
}