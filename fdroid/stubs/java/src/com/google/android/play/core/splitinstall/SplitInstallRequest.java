// Stub for F-Droid builds of Chromium: the API surface Chromium uses, implemented as
// "not available". Licensed under the same terms as this repository.
package com.google.android.play.core.splitinstall;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class SplitInstallRequest {
    private final List<String> mModules;
    private final List<Locale> mLanguages;

    private SplitInstallRequest(List<String> modules, List<Locale> languages) {
        mModules = modules;
        mLanguages = languages;
    }

    public static Builder newBuilder() {
        return new Builder();
    }

    public List<String> getModuleNames() {
        return mModules;
    }

    public List<Locale> getLanguages() {
        return mLanguages;
    }

    public static class Builder {
        private final List<String> mModules = new ArrayList<>();
        private final List<Locale> mLanguages = new ArrayList<>();

        public Builder addModule(String moduleName) {
            mModules.add(moduleName);
            return this;
        }

        public Builder addLanguage(Locale language) {
            mLanguages.add(language);
            return this;
        }

        public SplitInstallRequest build() {
            return new SplitInstallRequest(mModules, mLanguages);
        }
    }
}
