// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.firebase;

public final class FirebaseOptions {
    private FirebaseOptions() {}

    public static final class Builder {
        public Builder setProjectId(String projectId) {
            return this;
        }

        public Builder setApplicationId(String applicationId) {
            return this;
        }

        public Builder setApiKey(String apiKey) {
            return this;
        }

        public FirebaseOptions build() {
            return new FirebaseOptions();
        }
    }
}
