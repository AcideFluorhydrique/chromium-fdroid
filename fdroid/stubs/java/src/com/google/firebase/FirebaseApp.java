// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.firebase;

import android.content.Context;

import java.util.ArrayList;
import java.util.List;

public class FirebaseApp {
    private static final List<FirebaseApp> sApps = new ArrayList<>();
    private final String mName;

    private FirebaseApp(String name) {
        mName = name;
    }

    public static synchronized List<FirebaseApp> getApps(Context context) {
        return new ArrayList<>(sApps);
    }

    public static synchronized FirebaseApp initializeApp(
            Context context, FirebaseOptions options, String name) {
        FirebaseApp app = new FirebaseApp(name);
        sApps.add(app);
        return app;
    }

    public String getName() {
        return mName;
    }
}
