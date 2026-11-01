package org.vekendian.nexus.modules;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import org.vekendian.nexus.api.ModuleInfo;

/**
 * Inflates nexus_module_card.xml and fills it in.
 *
 * <p>Two card shapes come out of one layout: the fixed executor card passes a
 * null {@code remove} and gets the remove control hidden, a script card passes
 * itself and gets a listener. Every view lookup is null-checked, because the
 * layout is ours but a card can also be inflated into a host whose theme or
 * density resolved an optional child away.
 */
final class ModuleCards {

    private ModuleCards() {
    }

    static void bind(LayoutInflater inflater, ViewGroup parent, int[] r,
                     String title, String meta, String desc, int descColor,
                     final ModuleInfo module) {
        View card;
        try {
            card = inflater.inflate(r[2], parent, false);
        } catch (Throwable t) {
            NexusHost.log("card inflate failed: " + ModuleLoader.describe(t));
            return;
        }
        if (card == null) {
            return;
        }
        // inflate(layout, parent, false) builds the card with the parent's
        // layout params but does NOT attach it. Without this line every card
        // was bound and then dropped, so a successfully imported module left
        // the list empty and the empty-state hidden -- indistinguishable from
        // "the module was not added".
        parent.addView(card);
        setText(card, r[3], title);
        setText(card, r[4], meta);
        setText(card, r[5], desc);
        setColor(card, r[5], descColor);

        View del = card.findViewById(r[6]);
        if (module == null) {
            // Infrastructure: no remove control on the executor card.
            if (del != null) {
                del.setVisibility(View.GONE);
            }
            return;
        }
        if (del != null) {
            del.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    NexusHost.onRemoveClicked(module);
                }
            });
        }
    }

    private static void setText(View card, int id, String text) {
        if (id == 0 || text == null) {
            return;
        }
        View v = card.findViewById(id);
        if (v instanceof TextView) {
            ((TextView) v).setText(text);
        }
    }

    /**
     * The status line's colour, when there is one.
     *
     * <p>Zero means "leave the layout's colour alone": a card with no state
     * to report has nothing to colour.
     */
    private static void setColor(View card, int id, int color) {
        if (id == 0 || color == 0) {
            return;
        }
        View v = card.findViewById(id);
        if (v instanceof TextView) {
            ((TextView) v).setTextColor(color);
        }
    }
}