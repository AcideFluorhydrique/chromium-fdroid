// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.review;

public class ReviewException extends RuntimeException {
    private final int mErrorCode;

    public ReviewException(int errorCode) {
        super("In-app review is not available, error " + errorCode);
        mErrorCode = errorCode;
    }

    public int getErrorCode() {
        return mErrorCode;
    }
}
