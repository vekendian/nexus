-- zip.lua - an importable module written in Lua
--
--   nexus.modules.install("/storage/emulated/0/#Vekendian/nexus/examples/import/zip.lua")
--   local zip = nexus.modules.import("zip")
--   print(zip.greet("Nexus"))
--   print(zip.slug("Hello World.lua"))
--
-- The whole file is the module: install() copies it into the module
-- storage, and import() loads it in YOUR script's environment (loadstring in
-- the caller's Globals), so it sees your globals and your gg. The chunk's
-- return value is what import() hands back -- a table makes it importable.
-- Anything it throws reaches you as (nil, message).
--
-- The Java counterpart lives next to this file (zip.java): a .jar/.dex with
-- @Export methods imports exactly like this and calls through Java.

local zip = {}

function zip.greet(name)
    return "hello from zip.lua, " .. tostring(name)
end

-- lower, strip non-path characters, underscores between words
function zip.slug(s)
    s = tostring(s):lower()
    s = s:gsub("[^%w%.]+", "_")
    s = s:gsub("^_+", ""):gsub("_+$", "")
    return s
end

return zip
