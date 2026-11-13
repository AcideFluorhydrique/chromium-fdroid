// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.firebase.messaging;

import android.content.Intent;

public final class RemoteMessage {
    private RemoteMessage() {}

    public String getFrom() {
        return null;
    }

    public Intent toIntent() {
        return new Intent();
    }
}
