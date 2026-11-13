// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall;

import com.google.android.play.core.splitinstall.model.SplitInstallSessionStatus;

import java.util.Collections;
import java.util.List;

public class SplitInstallSessionState {
    private SplitInstallSessionState() {}

    public int sessionId() {
        return 0;
    }

    public int status() {
        return SplitInstallSessionStatus.UNKNOWN;
    }

    public int errorCode() {
        return 0;
    }

    public List<String> moduleNames() {
        return Collections.emptyList();
    }

    public List<String> languages() {
        return Collections.emptyList();
    }
}
