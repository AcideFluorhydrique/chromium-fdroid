// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.review.model;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.SOURCE)
public @interface ReviewErrorCode {
    int NO_ERROR = 0;
    int PLAY_STORE_NOT_FOUND = -1;
    int INVALID_REQUEST = -2;
    int INTERNAL_ERROR = -100;
}
