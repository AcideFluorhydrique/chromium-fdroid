// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.firebase.messaging;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public abstract class FirebaseMessagingService extends Service {
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    public void onMessageReceived(RemoteMessage message) {}

    public void onMessageSent(String msgId) {}

    public void onSendError(String msgId, Exception error) {}

    public void onDeletedMessages() {}

    public void onNewToken(String token) {}
}
