"""The MODULES tab: overlay FAB, SAF picker, prefs, card rendering.

These assert the shape of the generated smali and the XML assets. They cannot
assert that the picker opens or that a card renders on screen -- that needs a
device. What they do lock down is that every edit is emitted exactly once, that
the FAB is only visible on the MODULES tab, and that the SAF request is checked
ahead of GameGuardian's own onActivityResult dispatch.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from nexus.anchors import PatchError
from nexus.layout import MODULES_FAB, PANEL_MODULES, transform_main
from nexus.modules import (ONACTIVITYRESULT_ANCHOR, ONACTIVITYRESULT_NEW,
                           PREFS_KEY, PREFS_NAME, SAF_REQUEST,
                           modules_methods, transform_activity_result)

ANDROID = "{http://schemas.android.com/apk/res/android}"


def _ids():
    """A tiny Ids stand-in: enough for the modules templates."""

    class _I:
        def hex(self, name):
            return {
                "nexus_modules_list": "0x7f05017d",
                "nexus_modules_empty": "0x7f05017e",
                "nexus_module_tag": "0x7f050180",
                "nexus_module_title": "0x7f050181",
                "nexus_module_desc": "0x7f050183",
                "nexus_module_remove": "0x7f050184",
                "nexus_module_card": "0x7f06002f",
                "nexus_str_modules_none_loaded": "0x7f090369",
            }[name]
    return _I()


# ------------------------------------------------------------- XML assets ---

def test_fab_is_bottom_right_and_hidden_by_default():
    # The fragment is spliced into main.xml, so it carries no namespace of its
    # own; supply one so ElementTree can resolve the android: attributes.
    frag = ('<root xmlns:android="http://schemas.android.com/apk/res/android">'
            + MODULES_FAB + "</root>")
    root = list(ET.fromstring(frag))[0]
    assert root.get(ANDROID + "layout_gravity") == "bottom|end"
    assert root.get(ANDROID + "visibility") == "gone"
    assert root.get(ANDROID + "background") == "@drawable/nexus_bg_fab"
    assert root.get(ANDROID + "src") == "@drawable/nexus_ic_plus"
    assert root.get(ANDROID + "clickable") == "true"


def test_modules_panel_has_a_list_container_and_empty_state():
    assert "@+id/nexus_modules_list" in PANEL_MODULES
    assert "@+id/nexus_modules_empty" in PANEL_MODULES


# ------------------------------------------------------------- card layout ---

def test_card_layout_is_well_formed_and_has_the_four_fields():
    from nexus.tree import RES_DIR
    p = RES_DIR / "res/layout/nexus_module_card.xml"
    root = ET.fromstring(p.read_text(encoding="utf-8"))
    ids = {e.get(ANDROID + "id") for e in root.iter()}
    for want in ("@+id/nexus_module_tag", "@+id/nexus_module_title",
                 "@+id/nexus_module_meta", "@+id/nexus_module_desc",
                 "@+id/nexus_module_remove"):
        assert want in ids, want


def test_remove_control_is_a_sibling_not_a_child_of_the_text():
    """A nested remove button would let a long name push it off-card."""
    from nexus.tree import RES_DIR
    p = RES_DIR / "res/layout/nexus_module_card.xml"
    root = ET.fromstring(p.read_text(encoding="utf-8"))
    remove = [e for e in root.iter()
              if e.get(ANDROID + "id") == "@+id/nexus_module_remove"]
    assert len(remove) == 1
    assert remove[0] in list(root), "remove must be a direct child of the card root"


# ------------------------------------------------------------------- smali ---

def test_methods_interpolate_ids_and_prefs():
    out = modules_methods(_ids())
    assert "@@ID:" not in out and "@@PREFS@@" not in out and "@@REQ@@" not in out
    assert "0x7f05017d" in out            # nexus_modules_list
    assert "0x7f06002f" in out            # nexus_module_card layout
    assert f'"{PREFS_NAME}"' in out
    assert f'"{PREFS_KEY}"' in out
    assert SAF_REQUEST in out


def test_remove_method_is_public_for_the_listener_class():
    """r$ModuleRemove calls it via invoke-direct; private would not verify."""
    out = modules_methods(_ids())
    assert ".method public nexusModulesRemove(Ljava/lang/String;)V" in out


def test_render_toggles_the_empty_state_both_ways():
    """Children present -> GONE; no children -> VISIBLE."""
    out = modules_methods(_ids())
    m = re.search(r"\.method private nexusModulesRender\(\)V(.*?)\.end method", out, re.S)
    body = m.group(1)
    # The child-count branch must set both values, not the same one twice.
    assert "const/16 v5, 0x8" in body, "empty state must be hidden when cards exist"
    assert "const/4 v5, 0x0" in body, "empty state must be shown when no cards exist"


def test_remove_does_not_clobber_its_parameters():
    """2 params + .registers 9 leaves v0..v6 local; v7/v8 are p0/p1."""
    out = modules_methods(_ids())
    m = re.search(r"\.method public nexusModulesRemove\(Ljava/lang/String;\)V\n    \.registers (\d+)", out)
    assert m and int(m.group(1)) == 9
    body = out[m.end():out.index(".end method", m.end())]
    for reg in re.findall(r"\bv(\d+)\b", body):
        assert int(reg) <= 6, f"v{reg} would clobber a parameter register"


def test_query_uses_the_range_form():
    """ContentResolver.query takes receiver + 5 args, over the 5-register cap.

    The window must be {v0 .. v5} -- six registers, receiver low. It shipped as
    {v0 .. v6} (seven, receiver last) and ART rejected the class at load time;
    tests/test_invoke_arity.py now guards that arity repo-wide.
    """
    out = modules_methods(_ids())
    assert "invoke-virtual/range {v0 .. v5}," in out
    assert not re.search(r"invoke-virtual \{[^}]*,[^}]*,[^}]*,[^}]*,[^}]*,[^}]*\}", out)


# ------------------------------------------------------- onActivityResult ---

def test_aar_hook_precedes_gg_dispatch():
    # Split on the LABEL, not on any ":nexus_aar_gg" -- the guards reference it.
    head, _, tail = ONACTIVITYRESULT_NEW.partition("\n    :nexus_aar_gg\n")
    assert head, "label must exist"
    assert "nexusModulesAdd" in head, "our handler must be inside the guarded head"
    assert "return-void" in head, "our handler must return without touching GG"
    # The constant ends at the label: GG's body is whatever the anchor's own
    # text already was, and replace_once keeps it verbatim after our label.
    assert "b1;->F0" not in head, "GG's installer dispatch must not be in our head"
    assert not tail.strip(), "the replacement stops at the label"


def test_aar_hook_falls_through_on_any_mismatch():
    head = ONACTIVITYRESULT_NEW.partition("\n    :nexus_aar_gg\n")[0]
    for guard in ("if-ne p1, v0, :nexus_aar_gg",
                  "if-eqz p2, :nexus_aar_gg",
                  "if-eqz p3, :nexus_aar_gg"):
        assert guard in head, guard


def test_transform_activity_result_requires_the_anchor():
    body = ONACTIVITYRESULT_ANCHOR + "\n    return-void\n.end method\n"
    out = transform_activity_result(body)
    assert out.count("nexusModulesAdd") == 1
    with pytest.raises(PatchError):
        transform_activity_result(".method public other()V\n    .locals 0\n.end method\n")


# --------------------------------------------------------------- tab wiring ---

def test_overlay_wraps_scrollview_and_navbar():
    """The FAB needs a FrameLayout layer; ScrollView+navbar must be inside it."""
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    tree = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
                "Kujtnodnookc_499.2_src")
    src = tree / "res/layout/main.xml"
    if not src.is_file():
        pytest.skip("no stock GG tree on disk")
    out = transform_main(src.read_text(encoding="utf-8"), "1.0.0")
    assert "@+id/nexus_overlay" in out
    assert "@+id/nexus_shell" in out
    i_overlay = out.index("@+id/nexus_overlay")
    i_scroll = out.index("ScrollView", i_overlay)
    i_nav = out.index("@+id/nexus_navbar")
    i_fab = out.index("@+id/nexus_modules_add")
    assert i_overlay < i_scroll < i_nav, "overlay must open before both"
    assert i_fab > i_nav, "FAB is the overlay's second child, after the navbar"
