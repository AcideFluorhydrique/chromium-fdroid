// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.install.model;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.SOURCE)
public @interface UpdateAvailability {
    int UNKNOWN = 0;
    int UPDATE_NOT_AVAILABLE = 1;
    int UPDATE_AVAILABLE = 2;
    int DEVELOPER_TRIGGERED_UPDATE_IN_PROGRESS = 3;
}
