package org.vekendian.nexus.api;

/**
 * One loaded module, as the MODULES card needs to draw it. A dumb value class:
 * the Module Registry owns the state machine, the host owns the formatting, and
 * neither has to know about the other's fields.
 *
 * <p>State is an int rather than an enum so the host can map it to a pinned
 * string id without touching the Module Registry's classes.
 */
public final class ModuleInfo {

    public static final int STATE_IDLE = 0;
    public static final int STATE_RUNNING = 1;
    public static final int STATE_FINISHED = 2;
    public static final int STATE_STOPPED = 3;
    public static final int STATE_ERROR = 4;

    /** Module type: LUA (default), JAR, DEX. */
    public enum Type {
        LUA,
        JAR,
        DEX
    }

    /** Absolute path of the imported module. Doubles as the module's id. */
    private final String path;
    private final String name;
    private final String description;
    private final int version;
    private final int state;
    private final String message;
    private final long size;
    private final boolean autostart;
    private final Type type;
    private final String[] dependsOn;

    public ModuleInfo(String path, String name, String description, int version,
                         int state, String message, long size, boolean autostart,
                         Type type, String[] dependsOn) {
        this.path = path;
        this.name = name;
        this.description = description;
        this.version = version;
        this.state = state;
        this.message = message;
        this.size = size;
        this.autostart = autostart;
        this.type = type != null ? type : Type.LUA;
        this.dependsOn = dependsOn != null ? dependsOn : new String[0];
    }

    /** Backward-compatible constructor (defaults to LUA, empty deps). */
    public ModuleInfo(String path, String name, String description, int version,
                         int state, String message, long size, boolean autostart) {
        this(path, name, description, version, state, message, size, autostart,
             Type.LUA, new String[0]);
    }

    public String path() {
        return path;
    }

    /** Display name: the annotation's name, or the module id (no suffix). */
    public String name() {
        return name;
    }

    /** Annotation description, or the entry class name when there is none. */
    public String description() {
        return description;
    }

    public int version() {
        return version;
    }

    /** One of the STATE_* constants. */
    public int state() {
        return state;
    }

    /** Error text for STATE_ERROR, otherwise null. */
    public String message() {
        return message;
    }

    /** Size of the imported module in bytes. */
    public long size() {
        return size;
    }

    public boolean autostart() {
        return autostart;
    }

    /** Module type: LUA (default), JAR. */
    public Type type() {
        return type;
    }

    /** Module IDs this module depends on (filenames without .lua/.jar). */
    public String[] dependsOn() {
        return dependsOn;
    }
}