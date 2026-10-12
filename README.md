# Nexus patcher

<div align="center">
<table><tr><td align="left">
<pre>
  
                      .cc:;;,.                   ..
                     :xcdxxxxd.              .,lxc
                    :xxxcoxxxxx.           .oxxxl
                   cxxxx, lxxxxx.         .xxxxl
                  cxxxx'   lxxxxx'       .xxxxl
                 cxxxx'     lxxxxx,     .dxxxl
                :xxxx,       :xxxxx;   .dxxxc
               cxxxx,         ;xxxxx: .dxxxl
              cxxxx,           ,xxxxx;xxxxl
             cxxxx,             ;xxxldxxxl
            lxxxx'               ,x:dxxxl
           cxxxx;                 ,xxxxl
          cxxxo,                  'xxxl
         cd:'                      .xc
         .                          .
</pre>
</td></tr></table>
</div>

Re-skins GameGuardian as **Nexus** on any apktool-decoded GG tree: navbar and
card panels, a power card, an ENVIRONMENT readout, localised settings rows, a
modern dialog theme, a restyled keyboard, and a rebrand to
`org.vekendian.nexus` v1.0.0.

Bring your own GG APK. The patcher makes no network calls and touches nothing
outside the tree you point it at.

---

## Quick start

```bash
# 1. decode (apktool 2.8.1 + aapt2 is the known-good combo)
apktool d -f -s --aapt /usr/bin/aapt2 gg-499.2.apk -o gg_src

# 2. sanity-check the tree without modifying anything
python3 nexus.py check --src gg_src

# 3. patch (backs up first; safe to re-run after a revert)
python3 nexus.py apply --src gg_src

# 4. build a signed APK
bash build.sh --src gg_src --out nexus-1.0.0.apk

# 5. install
adb install -r nexus-1.0.0.apk
```

To go back:

```bash
python3 nexus.py revert --src gg_src
```

---

## Commands

| Command | What it does | Exit codes |
|---|---|---|
| `check --src T` | Read-only. Runs **preflight** on an unpatched tree, **postflight** on a patched one. | 0 pass · 1 fail · 2 bad input |
| `apply --src T` | Preflight, then patch. Refuses to touch the tree if preflight fails. | 0 ok · 1 abort · 2 bad input |
| `revert --src T` | Restores every file from `.nexus_backup/`, removes copied resources, then **verifies** nothing was left patched. | 0 ok · 1 nothing to do / incomplete · 2 bad input |
| `ids --src T` | Prints the ID lock file, resolves every GameGuardian binding against the tree, and reports drift. | 0 ok · 1 collision or missing binding |

## Why it fails loudly

Every edit targets an **exact literal block** copied from a known GG release. If
a weekly GG update changes one of those blocks, `check` fails with the name of
the anchor that drifted instead of producing an APK that is subtly wrong. That
is the intended behaviour — a loud failure costs a minute, a silent one costs a
debugging session.

`apply` runs preflight *before* writing anything, so a failed preflight leaves
the tree untouched.

---

## Resource IDs

`nexus_ids.json` is the lock file. It holds two very different kinds of ID:

**Nexus IDs** — the ids Nexus itself declares (view ids, drawables and strings).
These are **pinned**, so generated smali is byte-stable across rebuilds. If a
future GG release grows into this id range, preflight reports a collision and
they must be bumped.

**GameGuardian bindings** — views GG owns that Nexus attaches to (`id:check`,
`id:fix_it`, `id:language`, …). These are **resolved by name** from the tree's
`public.xml` at apply time, so a GG release that renumbers ids keeps working
with no code change.

`gg_observed` in the lock file records the hex each binding had in the GG
release the patcher was developed against. It is a **record, not a source of
truth**. If GG renumbers, `ids` reports the drift and the patch still succeeds.
If GG *removes* a view Nexus binds to, that is a hard error — silently binding
to something else would be much worse.

```bash
python3 nexus.py ids --src gg_src
```

```
Nexus id ids (29):
  0x7f050160  nexus_tab_home
  ...
GameGuardian bindings (resolved by name from public.xml):
  0x7f050025  check
  0x7f0500a5  help

Drift vs the recorded lock (expected on a new GG release; not fatal):
  - check: 0x7f050025 -> 0x7f050099
```

---

## Layout

```
nexus.py              thin entry point -> nexus.cli:main()
nexus/
  cli.py              argparse, dispatch, exit codes
  ids.py              ID resolver (nexus_ids.json lock file)
  anchors.py          PatchError, replace_once — the exact-anchor engine
  smali.py            all Nexus smali templates + render()
  layout.py           main.xml blocks: navbar, panels, ENVIRONMENT cards
  manifest.py         rebrand: package, label, version
  checks.py           preflight / postflight / ID audit
  tree.py             resolve_tree, backup, revert, read/write
nexus_ids.json        pinned IDs + observed GG bindings
resources/res/        static drawables, values, icons
tests/                pytest suite + fixtures
  make_fixture.py     regenerates the mini r.smali fixture from live anchors
build.sh              apktool b -> zipalign -> apksigner -> verify
```

Importing `nexus.*` is side-effect free, so the tests need no tree on disk.

---

## Tests

```bash
python3 -m pytest tests/ -q
```

If `pytest` is missing from your `python3`, note that Termux keeps its own
interpreter separate from `/usr/bin/python3`:

```bash
/data/data/com.termux/files/usr/bin/python3 -m pytest tests/ -q
```

`tests/fixtures/mini_r.smali` is generated from the live anchor constants by
`tests/make_fixture.py` — regenerate it after changing any anchor.

---

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `NEXUS_APKTOOL` | `apktool` on `PATH` | apktool jar, or a full path to one |
| `NEXUS_AAPT` | `aapt2` on `PATH` | aapt2 binary |
| `NEXUS_KEYSTORE` | `~/.android/debug.keystore` | signing key |
| `NEXUS_KEYALIAS` | `androiddebugkey` | signing alias |
| `NEXUS_KEYPASS` | `android` | signing password |

**Release signing:** the defaults are a *debug* key, fine for personal installs.
For a real release, set `NEXUS_KEYSTORE` / `NEXUS_KEYALIAS` / `NEXUS_KEYPASS`
to your own key. An APK signed with a different key than the installed one will
be rejected by `pm install -r`.

---

## Gotchas

- **Run `build.sh` with `bash`.** Android shared storage cannot set the exec
  bit, so `./build.sh` fails with a permission error.
- **`revert` restores only what `apply` touched.** If you hand-edit layouts,
  `revert` will not know about them. `revert` does scan for leftover Nexus
  markers afterwards and warns if it finds any.
- **Keep a pristine copy of your tree.** `.nexus_backup` is removed by a
  successful `revert`, and it is the only copy of the originals.
- **`MainService$m.smali` must keep the old download URL.** It uses that literal
  as `charAt(11) - 0x6a` to derive an array index, not as a URL. Rewriting it
  silently retargets a service-list button. `check` asserts this stays untouched.
