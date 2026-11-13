// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.review;

import android.content.Context;

public final class ReviewManagerFactory {
    private ReviewManagerFactory() {}

    public static ReviewManager create(Context context) {
        return new ReviewManager();
    }
}
