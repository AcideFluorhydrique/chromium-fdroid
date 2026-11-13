// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.install.model;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.SOURCE)
public @interface InstallStatus {
    int UNKNOWN = 0;
    int PENDING = 1;
    int DOWNLOADING = 2;
    int INSTALLING = 3;
    int INSTALLED = 4;
    int FAILED = 5;
    int CANCELED = 6;
    int REQUIRES_UI_INTENT = 10;
    int DOWNLOADED = 11;
}
