// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall.model;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.SOURCE)
public @interface SplitInstallSessionStatus {
    int UNKNOWN = 0;
    int PENDING = 1;
    int DOWNLOADING = 2;
    int DOWNLOADED = 3;
    int INSTALLING = 4;
    int INSTALLED = 5;
    int FAILED = 6;
    int CANCELED = 7;
    int REQUIRES_USER_CONFIRMATION = 8;
    int CANCELING = 9;
}
