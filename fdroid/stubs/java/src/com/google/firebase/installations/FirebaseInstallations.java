// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.firebase.installations;

import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.firebase.FirebaseApp;

public class FirebaseInstallations {
    private FirebaseInstallations() {}

    public static FirebaseInstallations getInstance(FirebaseApp app) {
        return new FirebaseInstallations();
    }

    public Task<String> getId() {
        return Tasks.forException(new UnsupportedOperationException("Firebase is not available"));
    }

    public Task<Void> delete() {
        return Tasks.forException(new UnsupportedOperationException("Firebase is not available"));
    }
}
