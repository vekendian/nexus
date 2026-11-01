package org.vekendian.nexus.modules;

import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Nexus's own toast.
 *
 * <p>A stock Android toast is a white rounded rectangle with the platform's
 * typography: the one surface in the app that still belongs to another app.
 * This is the reference app's toast -- a dark pill with a status dot -- built
 * as a window instead of a view, because Nexus has to be able to say things
 * from places an activity cannot reach.
 *
 * <p>That is the real reason this is not a Toast: GameGuardian's settings
 * list and its permission prompt are separate overlay windows, and a normal
 * toast is drawn *behind* an overlay. The feedback after a module is
 * installed would have been invisible exactly when the user needed it. The
 * window here is the same kind of overlay the dialogs use, so it lands on top.
 */
final class NexusToast {

    /** Neutral feedback. */
    static final int NEUTRAL = 0;
    /** Something worked. */
    static final int OK = 1;
    /** Something failed. */
    static final int ERROR = 2;

    private static final long SHORT_MS = 1600L;
    private static final long LONG_MS = 2600L;

    private NexusToast() {
    }

    static void show(Context context, String message, int kind) {
        if (context == null || message == null || message.length() == 0) {
            return;
        }
        final Context app = NexusHost.app() != null ? NexusHost.app() : context;
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            public void run() {
                present(app, message, kind);
            }
        });
    }

    private static void present(Context context, String message, int kind) {
        try {
            WindowManager wm = (WindowManager) context.getSystemService(
                    Context.WINDOW_SERVICE);
            if (wm == null) {
                return;
            }
            View pill = build(context, message, kind);
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    overlayType(),
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                            | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
                    android.graphics.PixelFormat.TRANSLUCENT);
            lp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
            lp.y = -dp(context, 104);
            wm.addView(pill, lp);

            // Slide-in animation
            pill.setTranslationY(dp(context, 100));
            pill.setAlpha(0f);
            pill.animate()
                    .translationY(0)
                    .alpha(1f)
                    .setDuration(200)
                    .setInterpolator(new android.view.animation.DecelerateInterpolator())
                    .start();

            // Swipe-to-dismiss gesture
            pill.setOnTouchListener(new View.OnTouchListener() {
                private float startY;
                private long startTime;

                @Override
                public boolean onTouch(View v, android.view.MotionEvent event) {
                    switch (event.getAction()) {
                        case android.view.MotionEvent.ACTION_DOWN: {
                            startY = event.getRawY();
                            startTime = System.currentTimeMillis();
                            return true;
                        }
                        case android.view.MotionEvent.ACTION_MOVE: {
                            float deltaY = event.getRawY() - startY;
                            if (deltaY > 0) {
                                v.setTranslationY(dp(context, 50) * (deltaY / dp(context, 100)));
                            }
                            return true;
                        }
                        case android.view.MotionEvent.ACTION_UP:
                        case android.view.MotionEvent.ACTION_CANCEL: {
                            float deltaY = event.getRawY() - startY;
                            long duration = System.currentTimeMillis() - startTime;
                            if (deltaY > dp(context, 50) || (deltaY > dp(context, 20) && duration < 200)) {
                                dismissWithAnimation(pill, wm);
                            } else {
                                v.animate()
                                        .translationY(0)
                                        .setDuration(150)
                                        .start();
                            }
                            return true;
                        }
                    }
                    return false;
                }
            });

            final Handler handler = new Handler(Looper.getMainLooper());
            handler.postDelayed(new Runnable() {
                public void run() {
                    dismissWithAnimation(pill, wm);
                }
            }, kind == NEUTRAL ? SHORT_MS : LONG_MS);
        } catch (Throwable t) {
            NexusHost.log("toast failed: " + ModuleLoader.describe(t));
        }
    }

    private static void dismissWithAnimation(View pill, WindowManager wm) {
        if (pill == null || wm == null) return;
        pill.animate()
                .translationY(dp(pill.getContext(), 100))
                .alpha(0f)
                .setDuration(150)
                .setInterpolator(new android.view.animation.AccelerateInterpolator())
                .withEndAction(() -> {
                    try {
                        wm.removeView(pill);
                    } catch (Throwable ignored) {}
                })
                .start();
    }

    private static View build(Context context, String message, int kind) {
        LinearLayout pill = new LinearLayout(context);
        pill.setOrientation(LinearLayout.HORIZONTAL);
        pill.setGravity(Gravity.CENTER_VERTICAL);
        int bg = NexusHost.resourceId(context, "nexus_bg_toast", "drawable");
        if (bg != 0) {
            pill.setBackgroundResource(bg);
        }
        pill.setPadding(dp(context, 16), dp(context, 12), dp(context, 20),
                dp(context, 12));
        pill.setElevation(dp(context, 8));

        View dot = new View(context);
        GradientDrawable shape = new GradientDrawable();
        shape.setShape(GradientDrawable.OVAL);
        shape.setColor(dotColor(context, kind));
        dot.setBackground(shape);
        LinearLayout.LayoutParams dotParams = new LinearLayout.LayoutParams(
                dp(context, 8), dp(context, 8));
        dotParams.rightMargin = dp(context, 12);
        pill.addView(dot, dotParams);

        TextView text = new TextView(context);
        text.setText(message);
        int colour = NexusHost.resourceId(context, "nexus_text", "color");
        if (colour != 0) {
            text.setTextColor(colour);
        }
        text.setTextSize(14f);
        text.setMaxWidth(dp(context, 280));
        pill.addView(text);

        FrameLayout frame = new FrameLayout(context);
        frame.addView(pill);
        return frame;
    }

    /**
     * The dot's colour: green for ok, red for a failure, orange otherwise.
     *
     * <p>Orange is the accent, so a neutral message wears it and nothing else
     * in the toast does.
     */
    private static int dotColor(Context context, int kind) {
        String name = kind == OK ? "nexus_ok" : kind == ERROR ? "nexus_bad"
                : "nexus_orange";
        int id = NexusHost.resourceId(context, name, "color");
        if (id != 0) {
            try {
                return context.getResources().getColor(id);
            } catch (Throwable t) {
                // Fall through to the literal below.
            }
        }
        return kind == OK ? 0xff4ade80 : kind == ERROR ? 0xffff5c5c : 0xffff7a00;
    }

    private static int overlayType() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            return WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        }
        return WindowManager.LayoutParams.TYPE_PHONE;
    }

    private static int dp(Context context, int value) {
        return (int) (value * context.getResources().getDisplayMetrics().density
                + 0.5f);
    }
}