"""Decoder-format independence.

GameGuardian's tree can be decoded by MT Manager or by apktool, and the two
disagree on formatting only: MT Manager puts each XML attribute on its own
line and writes `.registers N`, apktool collapses attributes onto the
element's line and writes `.locals N`. Every edit must work against either,
and must still fail loudly when GameGuardian actually changes something.
"""

from __future__ import annotations

import pytest

from nexus.anchors import PatchError, anchor_count, cut_once, replace_exact, replace_once
from nexus.smali import widen_onclick_frame

# The same anchor as a decoder would write it, in both styles.
PRETTY = '''\
<activity
    android:label="Game"
    android:name="com.scmq.ActivityMain">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
    </intent-filter>
</activity>'''

INLINE = ('<activity android:label="Game" android:name="com.scmq.ActivityMain">'
          '<intent-filter>'
          '<action android:name="android.intent.action.MAIN" />'
          '</intent-filter>'
          '</activity>')

ACTION_PRETTY = 'android:name="android.intent.action.MAIN"'
ACTION_INLINE = 'android:name="android.intent.action.MAIN"'


@pytest.mark.parametrize("text", [PRETTY, INLINE])
def test_anchor_matches_either_decoder(text):
    assert anchor_count(text, ACTION_PRETTY) == 1


@pytest.mark.parametrize("text", [PRETTY, INLINE])
def test_replace_once_splices_correctly(text):
    out = replace_once(text, ACTION_PRETTY, 'android:name="X"', "action")
    assert out.count('android:name="X"') == 1
    # The rest of the element survives untouched.
    assert "ActivityMain" in out
    assert "intent-filter" in out


def test_replace_once_rejects_duplicates():
    """Whitespace tolerance must not weaken the exactly-once rule."""
    dup = ACTION_PRETTY + "\n" + ACTION_PRETTY
    with pytest.raises(PatchError):
        replace_once(dup, ACTION_PRETTY, "x", "action")


def test_attribute_reordering_is_not_tolerated():
    """Only whitespace is ignored, so a real attribute change still fails."""
    reordered = '<activity android:name="com.scmq.ActivityMain" android:label="Game">'
    assert anchor_count(reordered, 'android:label="Game" android:name="com.scmq.ActivityMain"') == 0


def test_value_change_still_fails():
    """A renamed resource is a GG change, not a formatting difference."""
    drifted = PRETTY.replace('android.intent.action.MAIN', 'android.intent.action.VIEW')
    assert anchor_count(drifted, ACTION_PRETTY) == 0
    with pytest.raises(PatchError):
        replace_once(drifted, ACTION_PRETTY, "x", "action")


def test_cut_once_removes_block():
    out = cut_once(PRETTY, '<intent-filter>\n        '
                            '<action android:name="android.intent.action.MAIN" />\n'
                            '    </intent-filter>', "filter")
    assert "intent-filter" not in out
    assert "ActivityMain" in out


def test_replace_exact_handles_repeats_in_both_styles():
    block = ('<android.fix.LinearLayout android:layout_width="fill_parent" '
             'android:layout_height="wrap_content" '
             'android:baselineAligned="false">')
    text = block + "\n" + block.replace("\n", " ")
    assert anchor_count(text, block) == 2
    out = replace_exact(text, block, block + ' android:visibility="gone"', "rows", count=2)
    assert out.count('android:visibility="gone"') == 2


def test_replace_exact_wrong_count_fails():
    with pytest.raises(PatchError):
        replace_exact(INLINE, ACTION_PRETTY, "x", "action", count=2)


# ------------------------------------------------------------- registers ---

@pytest.mark.parametrize("directive,before,after", [
    (".registers", 4, 12),   # MT Manager: params + locals
    (".locals", 2, 10),      # apktool: locals only, params implied
])
def test_widen_onclick_frame_keeps_decoder_spelling(directive, before, after):
    src = f".method public onClick(Landroid/view/View;)V\n    {directive} {before}\n"
    out = widen_onclick_frame(src)
    assert f"    {directive} {after}" in out
    assert out.startswith(".method public onClick(Landroid/view/View;)V\n")


def test_widen_onclick_frame_is_idempotent_per_call():
    """Applying it twice to the same input gives the same single widening."""
    src = ".method public onClick(Landroid/view/View;)V\n    .locals 2\n"
    once = widen_onclick_frame(src)
    assert widen_onclick_frame(once).count(".locals") == 1
    assert ".locals 10" in once


def test_widen_onclick_frame_without_method_fails():
    with pytest.raises(PatchError):
        widen_onclick_frame(".method public onPause()V\n    .locals 0\n")
