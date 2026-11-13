// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.appupdate;

import android.app.Activity;
import android.content.IntentSender;

import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.android.play.core.install.InstallStateUpdatedListener;

public class AppUpdateManager {
    AppUpdateManager() {}

    public Task<AppUpdateInfo> getAppUpdateInfo() {
        return Tasks.forException(new UnsupportedOperationException("In-app updates are not available"));
    }

    public Task<Void> completeUpdate() {
        return Tasks.forException(new UnsupportedOperationException("In-app updates are not available"));
    }

    public void registerListener(InstallStateUpdatedListener listener) {}

    public void unregisterListener(InstallStateUpdatedListener listener) {}

    public boolean startUpdateFlowForResult(
            AppUpdateInfo appUpdateInfo, Activity activity, AppUpdateOptions options, int requestCode)
            throws IntentSender.SendIntentException {
        return false;
    }

    public boolean startUpdateFlowForResult(
            AppUpdateInfo appUpdateInfo, int appUpdateType, Activity activity, int requestCode)
            throws IntentSender.SendIntentException {
        return false;
    }
}
