// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.install.model;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.SOURCE)
public @interface InstallErrorCode {
    int NO_ERROR = 0;
    int ERROR_API_NOT_AVAILABLE = -3;
    int ERROR_PLAY_STORE_NOT_FOUND = -9;
    int ERROR_INTERNAL_ERROR = -100;
}
