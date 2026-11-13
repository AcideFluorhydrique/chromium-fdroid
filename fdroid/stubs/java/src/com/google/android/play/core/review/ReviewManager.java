// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.review;

import android.app.Activity;

import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.android.play.core.review.model.ReviewErrorCode;

public class ReviewManager {
    ReviewManager() {}

    public Task<ReviewInfo> requestReviewFlow() {
        return Tasks.forException(new ReviewException(ReviewErrorCode.PLAY_STORE_NOT_FOUND));
    }

    public Task<Void> launchReviewFlow(Activity activity, ReviewInfo reviewInfo) {
        return Tasks.forResult(null);
    }
}
