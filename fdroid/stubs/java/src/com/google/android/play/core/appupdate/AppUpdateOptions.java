// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.appupdate;

public final class AppUpdateOptions {
    private final int mAppUpdateType;

    private AppUpdateOptions(int appUpdateType) {
        mAppUpdateType = appUpdateType;
    }

    public static AppUpdateOptions defaultOptions(int appUpdateType) {
        return new AppUpdateOptions(appUpdateType);
    }

    public int appUpdateType() {
        return mAppUpdateType;
    }
}
