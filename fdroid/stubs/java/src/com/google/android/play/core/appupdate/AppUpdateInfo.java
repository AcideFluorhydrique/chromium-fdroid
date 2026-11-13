// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.appupdate;

import com.google.android.play.core.install.model.InstallStatus;
import com.google.android.play.core.install.model.UpdateAvailability;

public class AppUpdateInfo {
    private AppUpdateInfo() {}

    public int updateAvailability() {
        return UpdateAvailability.UNKNOWN;
    }

    public int installStatus() {
        return InstallStatus.UNKNOWN;
    }

    public boolean isUpdateTypeAllowed(AppUpdateOptions options) {
        return false;
    }

    public boolean isUpdateTypeAllowed(int appUpdateType) {
        return false;
    }

    public int availableVersionCode() {
        return 0;
    }
}
