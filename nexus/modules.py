"""The MODULES tab runtime: SAF picker, persistence, card rendering.

Everything here is smali injected into GG's `android/ext/r` (the activity
superclass both MainActivity and ActivityMain extend). The pieces:

    nexusModulesPick()          fire ACTION_OPEN_DOCUMENT
    onActivityResult hook       catch our request code, hand the Uri over
    nexusModulesAdd(Uri)        persist the Uri, re-render
    nexusModulesRemove(String)  drop a Uri, re-render
    nexusModulesRender()        prefs -> one card per Uri
    nexusModulesCard(...)       inflate + fill a single card
    nexusModulesName(String)    ContentResolver display name, path-tail fallback

Storage is one SharedPreferences file, `nexus_modules`, holding a
newline-delimited list of Uri strings under the key `uris`. Deliberately not
GameGuardian's own prefs file: mixing keys into GG's config risks confusing its
loader, and a separate file is trivially clearable by the user.

This stage only records modules. Nothing here loads or executes a dex -- that
arrives with the module engine, which will need a real file rather than a
content Uri. Cards are rendered from the persisted list so the tab is useful
(and testable) before any of that exists.
"""

from __future__ import annotations

import re

from .anchors import PatchError, replace_once

# "NX". GG's own startActivityForResult codes are computed from fields rather
# than literals, so a collision cannot be ruled out by reading the tree. This
# code is checked FIRST and any mismatch falls through untouched to GG's own
# installer dispatch, so a collision would surface as a picker that does not
# open rather than as a stolen install result.
SAF_REQUEST = "0x4e58"

PREFS_NAME = "nexus_modules"
PREFS_KEY = "uris"

# GG's onActivityResult logs, calls super, then dispatches to the installer
# when r.d is set. Our check goes in at the very top and returns early, so it
# can never consume GG's result.
ONACTIVITYRESULT_ANCHOR = '''\
.method protected onActivityResult(IILandroid/content/Intent;)V
    .locals 2'''

ONACTIVITYRESULT_NEW = f'''\
.method protected onActivityResult(IILandroid/content/Intent;)V
    .locals 2

    const v0, {SAF_REQUEST}

    if-ne p1, v0, :nexus_aar_gg

    if-eqz p2, :nexus_aar_gg

    if-eqz p3, :nexus_aar_gg

    invoke-virtual {{p3}}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object v0

    invoke-direct {{p0, v0}}, Landroid/ext/r;->nexusModulesAdd(Landroid/net/Uri;)V

    return-void

    :nexus_aar_gg'''


MODULES_METHODS = r'''
.method private nexusModulesPrefs()Landroid/content/SharedPreferences;
    .registers 3

    const-string v0, "@@PREFS@@"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    return-object v0
.end method

.method private nexusModulesUris()Ljava/lang/String;
    .registers 4

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesPrefs()Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "@@KEY@@"

    const-string v2, ""

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method private nexusModulesSave(Ljava/lang/String;)V
    .registers 4

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesPrefs()Landroid/content/SharedPreferences;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "@@KEY@@"

    invoke-interface {v1, v2, p1}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->commit()Z

    return-void
.end method

.method private nexusModulesPick()V
    .registers 6

    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.OPEN_DOCUMENT"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v1, "*/*"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    const-string v1, "android.intent.category.OPENABLE"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;

    const/4 v1, 0x3

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v3, "application/octet-stream"

    aput-object v3, v1, v2

    const/4 v2, 0x1

    const-string v3, "application/java-archive"

    aput-object v3, v1, v2

    const/4 v2, 0x2

    const-string v3, "application/vnd.android.dex-archive"

    aput-object v3, v1, v2

    const-string v2, "android.intent.extra.MIME_TYPES"

    invoke-virtual {v0, v2, v1}, Landroid/content/Intent;->putExtra(Ljava/lang/String;[Ljava/lang/String;)Landroid/content/Intent;

    const v1, @@REQ@@

    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent;I)V

    return-void
.end method

.method private nexusModulesAdd(Landroid/net/Uri;)V
    .registers 8

    if-eqz p1, :nma_done

    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    const/4 v1, 0x1

    invoke-virtual {v0, p1, v1}, Landroid/content/ContentResolver;->takePersistableUriPermission(Landroid/net/Uri;I)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    :catchall_0
    invoke-direct {p0}, Landroid/ext/r;->nexusModulesUris()Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :nma_store

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v1

    if-eqz v1, :nma_store

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\n"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :nma_store
    invoke-direct {p0, v0}, Landroid/ext/r;->nexusModulesSave(Ljava/lang/String;)V

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesRender()V

    :nma_done
    return-void
.end method

.method public nexusModulesRemove(Ljava/lang/String;)V
    .registers 9

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesUris()Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :nmr_done

    const-string v2, "\n"

    invoke-virtual {v0, v2}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    array-length v2, v0

    const/4 v3, 0x0

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    :nmr_loop
    if-ge v3, v2, :nmr_join

    aget-object v4, v0, v3

    if-eqz v4, :nmr_next

    invoke-virtual {v4, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-nez v5, :nmr_next

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v6, "\n"

    invoke-virtual {v1, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :nmr_next
    add-int/lit8 v3, v3, 0x1

    goto :nmr_loop

    :nmr_join
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->length()I

    move-result v6

    if-eqz v6, :nmr_write

    invoke-virtual {v1, v6}, Ljava/lang/StringBuilder;->deleteCharAt(I)V

    :nmr_write
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, v0}, Landroid/ext/r;->nexusModulesSave(Ljava/lang/String;)V

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesRender()V

    :nmr_done
    return-void
.end method

.method private nexusModulesRender()V
    .registers 8

    const v0, @@ID:nexus_modules_list@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nmr_done

    check-cast v0, Landroid/view/ViewGroup;

    invoke-virtual {v0}, Landroid/view/ViewGroup;->removeAllViews()V

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesUris()Ljava/lang/String;

    move-result-object v1

    if-eqz v1, :nmr_show_empty

    invoke-virtual {v1}, Ljava/lang/String;->length()I

    move-result v2

    if-eqz v2, :nmr_show_empty

    const-string v2, "\n"

    invoke-virtual {v1, v2}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v1

    array-length v2, v1

    const/4 v3, 0x0

    :nmr_loop
    if-ge v3, v2, :nmr_check_empty

    aget-object v4, v1, v3

    if-eqz v4, :nmr_next

    invoke-virtual {v4}, Ljava/lang/String;->length()I

    move-result v5

    if-eqz v5, :nmr_next

    invoke-direct {p0, v0, v4}, Landroid/ext/r;->nexusModulesCard(Landroid/view/ViewGroup;Ljava/lang/String;)V

    :nmr_next
    add-int/lit8 v3, v3, 0x1

    goto :nmr_loop

    :nmr_check_empty
    invoke-virtual {v0}, Landroid/view/ViewGroup;->getChildCount()I

    move-result v2

    if-eqz v2, :nmr_show_empty

    const/16 v5, 0x8

    goto :nmr_apply_empty

    :nmr_show_empty
    const/4 v5, 0x0

    :nmr_apply_empty
    const v4, @@ID:nexus_modules_empty@@

    invoke-virtual {p0, v4}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v4

    if-eqz v4, :nmr_done

    invoke-virtual {v4, v5}, Landroid/view/View;->setVisibility(I)V

    :nmr_done
    return-void
.end method

.method private nexusModulesCard(Landroid/view/ViewGroup;Ljava/lang/String;)V
    .registers 10

    invoke-static {p0}, Landroid/view/LayoutInflater;->from(Landroid/content/Context;)Landroid/view/LayoutInflater;

    move-result-object v0

    const v1, @@ID:nexus_module_card@@

    const/4 v2, 0x0

    invoke-virtual {v0, v1, p1, v2}, Landroid/view/LayoutInflater;->inflate(ILandroid/view/ViewGroup;Z)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nmc_done

    invoke-direct {p0, p2}, Landroid/ext/r;->nexusModulesName(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    const v1, @@ID:nexus_module_tag@@

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v4

    if-eqz v4, :nmc_title

    check-cast v4, Landroid/widget/TextView;

    invoke-virtual {v4, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nmc_title
    const v1, @@ID:nexus_module_title@@

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v4

    if-eqz v4, :nmc_desc

    check-cast v4, Landroid/widget/TextView;

    invoke-virtual {v4, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nmc_desc
    const v1, @@ID:nexus_module_desc@@

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v4

    if-eqz v4, :nmc_remove

    check-cast v4, Landroid/widget/TextView;

    const v1, @@ID:nexus_str_modules_none_loaded@@

    invoke-virtual {p0, v1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v4, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nmc_remove
    const v1, @@ID:nexus_module_remove@@

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v4

    if-eqz v4, :nmc_add

    new-instance v5, Landroid/ext/r$ModuleRemove;

    invoke-direct {v5, p0, p2}, Landroid/ext/r$ModuleRemove;-><init>(Landroid/ext/r;Ljava/lang/String;)V

    invoke-virtual {v4, v5}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    :nmc_add
    invoke-virtual {p1, v0}, Landroid/view/ViewGroup;->addView(Landroid/view/View;)V

    :nmc_done
    return-void
.end method

.method private nexusModulesName(Ljava/lang/String;)Ljava/lang/String;
    .registers 10

    :try_start_0
    invoke-static {p1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v1

    # ContentResolver.query() takes receiver + 5 args = 6 registers, one more
    # than the non-range invoke form can encode, so it must use /range with a
    # CONTIGUOUS window whose FIRST register is the receiver. v0..v5 is that
    # window: v0 resolver, v1 Uri, v2 projection, v3/v4/v5 the null
    # selection/selectionArgs/sortOrder. The cursor lands in v6, outside it.
    invoke-virtual {p0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/String;

    const/4 v3, 0x0

    const-string v4, "_display_name"

    aput-object v4, v2, v3

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x0

    invoke-virtual/range {v0 .. v5}, Landroid/content/ContentResolver;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;

    move-result-object v6

    if-eqz v6, :nmn_fallback

    invoke-interface {v6}, Landroid/database/Cursor;->moveToFirst()Z

    move-result v3

    if-eqz v3, :nmn_close

    const/4 v3, 0x0

    invoke-interface {v6, v3}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v3

    invoke-interface {v6}, Landroid/database/Cursor;->close()V

    if-eqz v3, :nmn_fallback

    return-object v3

    :nmn_close
    invoke-interface {v6}, Landroid/database/Cursor;->close()V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    :catchall_0
    :nmn_fallback
    const/16 v3, 0x2f

    invoke-virtual {p1, v3}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v4

    if-ltz v4, :nmn_all

    add-int/lit8 v4, v4, 0x1

    invoke-virtual {p1, v4}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v3

    return-object v3

    :nmn_all
    return-object p1
.end method
'''


def modules_methods(ids) -> str:
    """The nexusModules* helpers, with ids interpolated."""
    out = (MODULES_METHODS
           .replace("@@PREFS@@", PREFS_NAME)
           .replace("@@KEY@@", PREFS_KEY)
           .replace("@@REQ@@", SAF_REQUEST))
    return re.sub(r"@@ID:(\w+)@@", lambda m: ids.hex(m.group(1)), out)


def transform_activity_result(smali: str) -> str:
    """Hook the SAF result ahead of GG's own onActivityResult dispatch."""
    return replace_once(smali, ONACTIVITYRESULT_ANCHOR, ONACTIVITYRESULT_NEW,
                        "onActivityResult SAF hook")
