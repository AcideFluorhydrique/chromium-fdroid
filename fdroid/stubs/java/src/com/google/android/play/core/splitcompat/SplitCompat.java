// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitcompat;

import android.content.Context;

public final class SplitCompat {
    private SplitCompat() {}

    public static boolean install(Context context) {
        return true;
    }

    public static boolean installActivity(Context activity) {
        return true;
    }
}
