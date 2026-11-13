// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.install;

import com.google.android.play.core.install.model.InstallStatus;

public class InstallState {
    private InstallState() {}

    public int installStatus() {
        return InstallStatus.UNKNOWN;
    }

    public int installErrorCode() {
        return 0;
    }

    public String packageName() {
        return "";
    }
}
