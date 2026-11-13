// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.gms.iid;

import android.content.Context;
import android.os.Bundle;

import java.io.IOException;

public class InstanceID {
    private final String mSubtype;

    private InstanceID(String subtype) {
        mSubtype = subtype;
    }

    public static InstanceID getInstance(Context context, Bundle options) {
        String subtype = options == null ? "" : String.valueOf(options.getCharSequence("subtype", ""));
        return new InstanceID(subtype);
    }

    public String getSubtype() {
        return mSubtype;
    }

    public String getId() {
        return "";
    }

    public long getCreationTime() {
        return 0;
    }

    public void deleteInstanceID() throws IOException {}

    public void deleteToken(String authorizedEntity, String scope) throws IOException {}

    public String getToken(String authorizedEntity, String scope) throws IOException {
        throw new IOException("SERVICE_NOT_AVAILABLE");
    }
}
