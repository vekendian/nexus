# Nexus Lua API

Nexus adds one global table to every GameGuardian script: `nexus`. It is built
when the script starts, so there is nothing to require and nothing to install
before using it.

```lua
print(nexus.version)   --> 1.0.0
```

`nexus.version` is a **string**, and it exists in every script — even one that
runs before Nexus has finished booting. Only the categories that need the module
engine (`nexus.modules.*`) check whether it is running.

Written for GameGuardian **101.4** (Lua 5.3 / LuaJ 3.0.1). The patch also
exposes the `luajava` table and the `import` function, which jar/dex modules
need; `nexus` is the API table and the only Nexus-specific global.

---

## Contents

| Call | Returns |
| --- | --- |
| `nexus.modules.install(path)` | `true` or `nil, err` |
| `nexus.modules.install(path, metadata)` | `true` or `nil, err` |
| `nexus.modules.install{...}` | `true` or `nil, err` |
| `nexus.modules.uninstall(path)` | `true` or `nil, err` |
| `nexus.modules.list()` | table of records, or `nil, err` |
| `nexus.modules.import(id)` | module value, or `nil, err` |

Every failure returns two values: `nil` and a reason string. Nothing throws, so a
script can always continue:

```lua
local ok, err = nexus.modules.install('/sdcard/Download/zip.jar')
if not ok then
  print('install failed: ' .. err)
end
```

---

## Permissions

Every `nexus.modules.*` call is gated. The first time a script makes a call, a
dialog asks:

- **Deny**
- **Allow once**
- **Always allow**

"Always allow" is remembered for that script **and that capability**. Deny
returns `nil, "permission denied"` and the script keeps running.

The capabilities are:

| Capability | Covers |
| --- | --- |
| `modules.install` | `install` |
| `modules.uninstall` | `uninstall` |
| `modules.list` | `list` |
| `modules.import` | `import`, and every method of an imported module |

`import` is one capability on purpose: importing a module, reading its exports
and calling one of its methods are one action, so the user is asked once.

If Nexus has not started, no prompt is shown and the call returns
`nil, "module system is not running"` — the engine check always runs first.

Change remembered choices later in **floating Settings > Permissions**.

---

## `nexus.modules.install`

Copies a module into Nexus storage and registers it. Three shapes are accepted.

### 1. Path only

```lua
nexus.modules.install('/sdcard/Download/zip.jar')
```

The path must name a readable file. Nexus copies it into its own module
directory and registers the copy, so the path you pass is **not** the path you
get back — use the `path` field from `list()` for later calls.

### 2. Path plus metadata

```lua
nexus.modules.install('/sdcard/Download/hello.lua', {
  name        = 'Hello',        -- display label (list().name)
  description = 'Says hello',   -- free text
  version     = '3',            -- integer, as a string
  type        = 'lua',          -- ignored here; the suffix decides
})
```

The explicit path wins over any `path` key in the table.

### 3. Raw bytes

```lua
local f = io.open('/sdcard/Download/hello.lua', 'rb')
local src = f:read('*a')
f:close()

nexus.modules.install{
  content     = src,            -- a Lua string of raw bytes
  name        = 'hello.lua',    -- also derives the module id
  description = 'Says hello',
  version     = '1',
  type        = 'lua',          -- 'lua', 'jar' or 'dex'
}
```

`content` must be a Lua string (binary-safe); anything else is ignored and the
call falls back to `path`. When `content` is present it wins over `path`;
`install{path = '...'}` is the same as shape 2.

- `name` also determines the module id. Without a `name`, the id becomes
  `module`, so always pass one for byte installs.
- `type` is used **only** for byte installs, to choose the stored suffix
  (`.lua`, `.jar`, `.dex`, case-insensitive). Path installs detect the type from
  the file's suffix.
- `version` must be a string or number that parses as an integer. Absent or
  empty means `0`. A version of `0` does not override a version declared by the
  module's manifest.

### Metadata keys

| Key | Type | Effect |
| --- | --- | --- |
| `name` | string | Display label. Defaults to the id; a custom `name` is used verbatim. |
| `description` | string | Free text shown in `list()`. Empty is ignored. |
| `version` | string | Integer version. Only stored when greater than `0`. |
| `type` | string | `lua`, `jar` or `dex`. Byte installs only. |

Installing a module that is already installed is a no-op: the first copy wins
and the call still returns `true`.

### Errors

- `cannot read <path>` — the path is missing, not a file, or unreadable
- `version must be an integer` — `version` did not parse
- `empty module content` — `content` was an empty string
- `missing module path` — no path and no content
- `module could not be imported (expected .lua, .jar or .dex)` — path install rejected
- `module could not be imported` — byte install rejected
- `permission denied`
- `module system is not running`

A rejected install leaves no file and no record behind.

---

## `nexus.modules.uninstall`

```lua
nexus.modules.uninstall('/data/.../files/modules/zip.jar')
```

Takes the **exact full path** of a registered module, as returned by `list()`.
A bare id (`"zip"`) is not accepted — use `row.path` from `list()`:

```lua
local rows = nexus.modules.list()
for _, row in ipairs(rows) do
  if row.id == 'zip' then
    nexus.modules.uninstall(row.path)
  end
end
```

### Errors

- `no module at <path>` — nothing is registered at that exact path
- `module could not be removed` — the engine refused the removal
- `missing module path` — no argument
- `permission denied`
- `module system is not running`

---

## `nexus.modules.list`

```lua
local rows = nexus.modules.list()
for _, row in ipairs(rows) do
  print(row.id, row.type, row.state, row.version, row.path)
end
```

Returns a 1-based array of records. Zero modules gives an empty table, not
`nil`.

### Record fields

| Field | Type | Meaning |
| --- | --- | --- |
| `path` | string | Full path of the stored copy. Pass this to `uninstall`. |
| `name` | string | Display label, the module id by default; a custom `name` is used as given. |
| `id` | string | File name without its suffix. This is what `import()` takes. |
| `state` | string | `idle`, `running`, `finished`, `stopped` or `error`. |
| `version` | string | The integer version as text; `"0"` when unset. |
| `autostart` | boolean | Whether the module starts with Nexus. |
| `type` | string | `lua`, `jar` or `dex`. |
| `description` | string | Free text; `""` when empty. |
| `message` | string | Last error text; `""` when none. |

Tabs and newlines inside text fields are replaced with spaces so a record can
never be mis-split.

### Errors

- `permission denied`
- `module system is not running`

---

## `nexus.modules.import`

Loads a registered module and returns its value.

```lua
local zip = nexus.modules.import('zip')
```

The argument is the module **id** — the file name minus `.lua`, `.jar` or
`.dex` — or a full registered path. Both resolve; the bare id is the usual form.

### Lua modules

The module's source runs immediately, in the caller's own environment, with the
chunk name `nexus.modules.import:<id>`. `import()` returns whatever the chunk
returns, so a module conventionally ends with `return M`:

```lua
-- zip.lua
local M = {}
function M.compress(dir, level)
  -- ...
end
return M
```

```lua
local zip = nexus.modules.import('zip')
zip.compress('/sdcard/Download/folder', 5)
```

A chunk that returns nothing gives `nil` — that is not an error.

### JAR and DEX modules

`import()` returns a table containing:

1. **One function per `@Export` method**, stored as real keys, so
   `mod.compress(...)` calls the exported method directly.
2. **Classes**, resolved lazily through the table's metatable. `mod.Probe` looks
   up `<id>.Probe` first, then bare `Probe`, so a class in package `mod` is
   reached as `mod.Probe` without any `luajava` call. A miss is `nil`, never an
   error, so `if mod.Maybe then` is safe.

A jar/dex with no `@Export` methods still imports: you get the class table.

Classes in another package stay reachable with
`luajava.bindClass('com.example.Probe')`.

### Calling exported methods

Arguments are plain Lua values:

| Parameter | Lua value |
| --- | --- |
| `String` | string |
| `int` | a whole number, or a string that parses as one |
| `double` | number, or a numeric string |
| `boolean` | `true` / `false` |
| `String[]` (varargs) | the remaining arguments, at the end |

A `nil` argument is passed as an empty string. Fractional values do not satisfy
an `int` parameter.

Return values are re-typed from the declared return type:

| Declared return | Lua value |
| --- | --- |
| `void` | `true` |
| `String` | string |
| numeric | number |
| `boolean` | boolean |

A failed call returns `nil, err`, with the reason from the engine, for example:

- `method not exported: <name>`
- `arity mismatch: expected at least N args, got M`
- `argument N type mismatch: ...`
- `method signature mismatch`
- `no entry instance`
- `interrupted` — the script was stopped
- `malformed result from module`
- `not a number returned by module: ...`

### Errors

- `no module at <id>` — no registered module has that id or path
- `nothing importable at <id>` — the module exists but has no exports, no
  classes and no Lua source
- `permission denied`
- `module system is not running`
- a load error, such as `luaj.LuaError: ...` from a broken Lua module

---

## Complete error reference

| Message | Where |
| --- | --- |
| `permission denied` | every gated call, after Deny |
| `module system is not running` | every `nexus.modules.*` call before Nexus starts |
| `missing module path` | `install` with no path and no content |
| `cannot read <path>` | `install(path)`, unreadable file |
| `version must be an integer` | `install`, bad `version` |
| `empty module content` | `install{content=...}`, empty string |
| `module could not be imported (expected .lua, .jar or .dex)` | `install(path)`, rejected file |
| `module could not be imported` | `install{content=...}`, rejected bytes |
| `no module at <path or id>` | `uninstall`, `import` |
| `module could not be removed` | `uninstall` |
| `nothing importable at <id>` | `import` |

---

## Examples

### Install, list, remove

```lua
local ok, err = nexus.modules.install('/sdcard/Download/zip.jar', {
  name        = 'Zip',
  description = 'Archive helpers',
  version     = '2',
})
if not ok then
  print(err)
  return
end

for _, row in ipairs(nexus.modules.list()) do
  print(row.id .. ' [' .. row.type .. '] ' .. row.state)
  if row.id == 'zip' then
    nexus.modules.uninstall(row.path)
  end
end
```

### Install a module from bytes

```lua
local f = io.open('/sdcard/Download/hello.lua', 'rb')
local src = f:read('*a')
f:close()

local ok, err = nexus.modules.install{
  content = src,
  name    = 'hello.lua',
  version = '1',
  type    = 'lua',
}
print(ok and 'installed' or err)
```

### Import a Lua module

```lua
local zip = nexus.modules.import('zip')
if not zip then
  print('zip is not installed')
  return
end
zip.compress('/sdcard/Download/folder', 5)
```

### Import a jar and build one of its classes

```lua
local probe = nexus.modules.import('probe')
local p = probe.Probe('hello')   -- package probe.Probe
print(p)

local other = luajava.bindClass('com.example.Other')
```

### Inspect state after a failed run

```lua
for _, row in ipairs(nexus.modules.list()) do
  if row.state == 'error' then
    print(row.id .. ': ' .. row.message)
  end
end
```

---

## Notes

- `install` copies the file. The returned `path` in `list()` is the copy in
  Nexus's own storage, not the original document.
- Module ids are the stored file name minus `.lua`, `.jar` or `.dex`. Two files
  with the same base name are the same module: the second install is skipped.
- `nexus.modules` may be missing if the namespace failed to attach at script
  start; `nexus.version` is still readable in that case.
- `uninstall` matches the full path exactly; `import` accepts an id or a full
  path.
- `list()` reports `version` as a string because the engine stores it as an
  integer.
