// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.appupdate;

import android.content.Context;

public final class AppUpdateManagerFactory {
    private AppUpdateManagerFactory() {}

    public static AppUpdateManager create(Context context) {
        return new AppUpdateManager();
    }
}
