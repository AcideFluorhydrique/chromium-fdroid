// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall;

public class SplitInstallException extends RuntimeException {
    private final int mErrorCode;

    public SplitInstallException(int errorCode) {
        super("Split install is not available, error " + errorCode);
        mErrorCode = errorCode;
    }

    public int getErrorCode() {
        return mErrorCode;
    }
}
