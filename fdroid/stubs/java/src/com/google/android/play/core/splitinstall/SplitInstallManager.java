// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall;

import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.android.play.core.splitinstall.model.SplitInstallErrorCode;

import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class SplitInstallManager {
    SplitInstallManager() {}

    public void registerListener(SplitInstallStateUpdatedListener listener) {}

    public void unregisterListener(SplitInstallStateUpdatedListener listener) {}

    public Task<Integer> startInstall(SplitInstallRequest request) {
        return Tasks.forException(new SplitInstallException(SplitInstallErrorCode.API_NOT_AVAILABLE));
    }

    public Task<Void> deferredInstall(List<String> moduleNames) {
        return Tasks.forException(new SplitInstallException(SplitInstallErrorCode.API_NOT_AVAILABLE));
    }

    public Task<Void> deferredLanguageInstall(List<Locale> languages) {
        return Tasks.forException(new SplitInstallException(SplitInstallErrorCode.API_NOT_AVAILABLE));
    }

    public Task<Void> deferredUninstall(List<String> moduleNames) {
        return Tasks.forException(new SplitInstallException(SplitInstallErrorCode.API_NOT_AVAILABLE));
    }

    public Set<String> getInstalledModules() {
        return Collections.emptySet();
    }

    public Set<String> getInstalledLanguages() {
        return Collections.emptySet();
    }
}
