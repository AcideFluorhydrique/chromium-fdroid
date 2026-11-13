// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall;

import android.content.Context;

public final class SplitInstallManagerFactory {
    private SplitInstallManagerFactory() {}

    public static SplitInstallManager create(Context context) {
        return new SplitInstallManager();
    }
}
