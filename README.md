# chromium-fdroid

An experimental project to investigate whether Chromium for Android can be built from source in compliance with [F-Droid's Inclusion Policy](https://f-droid.org/docs/Inclusion_Policy/).

The findings and progress are reported in [fdroiddata#3911](https://gitlab.com/fdroid/fdroiddata/-/work_items/3911).

**This repository is for experimentation only. It does not distribute APKs.** Regular Chromium builds are published at [AcideFluorhydrique/chromium](https://github.com/AcideFluorhydrique/chromium).

## Running a Build

Go to **Actions → Build Chromium Android for F-Droid tests → Run workflow**.

Workflow inputs:

- `version`: Chromium version tag. Leave empty to use the latest Android Stable release.
- `own_toolchain`: Build clang/lld, Rust/bindgen, GN, Ninja, and Node from source instead of using Google's prebuilt toolchains.
- `package_name`: Android package name. Defaults to `org.chromium.chrome.fdroidtest`, allowing the test build to be installed alongside the regular release.
- `toolchain_from`: Reuse a toolchain built by a previous workflow run, specified as `owner/repo/run_id`. Saves approximately 2.5 hours. Artifacts are retained for 7 days.

GitHub Actions free runners have a maximum execution time of 6 hours per job, so the build is split into multiple workflows:

1. **`toolchain.yml`**: Three parallel jobs build clang, Rust, and GN/Ninja/Node respectively. Takes approximately 2.5 hours.
2. **`stage.yml`**: Builds the APK using the same staged build process as the regular release. During Stage 1, prebuilt toolchains downloaded by `gclient sync` are replaced with the source-built versions from the first workflow. The job summary reports the versions and hashes of both toolchains for verification.

## Current Progress

| Task | Status |
|---|---|
| Build toolchain from source (clang, Rust, GN, Ninja, Node) | All components build successfully (clang: 1h42m, Rust: 2h25m, GN/Ninja/Node: 2h). Testing APK builds with these toolchains is ongoing. |
| Scan source tree with `fdroid scanner` and identify remaining prebuilt binaries | Completed for version 157.0.8103.50. See [reports/157.0.8103.50](reports/157.0.8103.50/fdroid-scan.md). |
| Generate `scandelete` rules from the build graph ([#3](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/3)) | 167 rules generated. Reduced 70,988 findings to 5,275 after applying the rules. See [build-graph.md](reports/157.0.8103.50/build-graph.md) and [scan-rules.txt](reports/157.0.8103.50/scan-rules.txt). |
| Review the flagged files the build reads ([#7](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/7)) | Done. 7 accepted in [`fdroid/scanignore.txt`](fdroid/scanignore.txt); 5 must be replaced and are assigned to #5, #6 and #8. See [`fdroid/build-graph-review.md`](fdroid/build-graph-review.md). |
| Replace prebuilt Android build tools with versions from `sdkmanager` / Maven (aapt2, bundletool, kotlinc, protoc, etc.); build R8 from source | Not started. |
| Replace the 443 Maven packages in `third_party/android_deps` and `androidx` | Not started. Can be handled in batches. |
| Remove non-open-source dependencies, including Google Play services, Firebase, ML Kit, and ARCore | Not started. |

## Scan Results (157.0.8103.50)

After `gclient sync`, the source tree contains 70,988 files flagged by the F-Droid scanner. Most of them are not actually needed to build the APK.

| Category | Files | Size | Proposed handling |
|---|---:|---:|---|
| Test, fuzzing, and benchmark data | 62,637 | 1.4 GB | Remove by directory using F-Droid metadata `scandelete` rules. |
| Toolchains, SDKs, and build tools | 4,638 | 5.4 GB | Build toolchains from source; replace SDK/NDK/JDK with versions from `sdkmanager` and Debian. |
| Other: tools used only for testing or development (Robolectric, Espresso, CTS, Apache, CPython 3, luci-go, etc.) | 161 | 8.1 GB | Exclude from sync or remove. |
| Other: small data files (under 64 KB), such as phone number databases and test vectors | 2,728 | 4.7 MB | Review individually and add to `scanignore`. |
| Other: larger files (DevTools frontend, OpenScreen, Dawn, ANGLE, etc.) | 341 | 1.2 GB | Require individual review. |
| Java packages (`androidx`, `android_deps`) | 360 | 178 MB | Fetch from Maven or build from source. |
| References to non-open-source dependencies (Play services, Firebase, ML Kit, unknown Maven repositories) | 123 | 3.6 MB | Remove through patches. |

The complete findings are available in [`fdroid-scan-findings.tsv.gz`](reports/157.0.8103.50/fdroid-scan-findings.tsv.gz).

Columns include category, type, path, size, and whether the file is accessed during the build.

### After Applying `scandelete` and `scanignore` Rules

`scan.yml` first runs `ninja -t inputs chrome_public_apk` to enumerate the files required to build the APK.

Files flagged by the scanner but not accessed during the build are automatically grouped into [167 `scandelete` rules](reports/157.0.8103.50/scan-rules.txt). Flagged files the build does read were reviewed by hand (#7); the ones accepted as source or data are listed in [`fdroid/scanignore.txt`](fdroid/scanignore.txt). The scanner is then run again with both lists applied. Numbers below are for 157.0.8103.78; 157.0.8103.50 gives the same rules and counts.

| Category | Before | After |
|---|---:|---:|
| Test, fuzzing, and benchmark data | 62,637 | 135 |
| Other | 3,230 | 12 |
| Toolchains, SDKs, and build tools | 4,638 | 4,638 |
| Java packages | 360 | 360 |
| References to non-open-source dependencies | 123 | 123 |
| **Total** | **70,988** | **5,268** |

Notes:

- The remaining 135 test/benchmark findings are all `executable binary, possibly code` warnings. They do not prevent the build.
- Of the 12 remaining files in the "Other" category, 7 are `executable binary, possibly code` warnings. The other 5 are prebuilt tools and libraries the build needs (TypeScript `tsc`, esbuild, gperf, `kotlin-stdlib-jdk8`, ARCore), listed in [`fdroid/build-graph-review.md`](fdroid/build-graph-review.md).
- Of the 360 Java package findings, 165 are not even required by `chrome_public_apk`.

**Important limitation:** `ninja -t inputs` only reports inputs explicitly declared in the GN build graph. Executables invoked directly by build scripts may not appear in its output. Therefore, this method is only used to determine whether test data and files in the "Other" category are actually needed. It is not used to exclude toolchains or build tools.

## Differences from Chromium's Official Toolchain

The source-built toolchain is not yet identical to Chromium's official toolchain:

- **Clang:** No bootstrap build, PGO, ThinLTO, or BOLT. The starting point is Ubuntu's clang-18.
- **Android RISC-V runtime:** Not built, as the NDK available on the runner does not yet support API level 37.
- **Rust:** Crubit is not built. The starting point is the official Rust stage0 compiler.
- **GN:** Built with GCC 13 because GN uses C++23's `std::expected`, which is not supported by clang-18 together with Ubuntu's libstdc++.
- **OpenSSL:** Rust's OpenSSL 3.5 dependency is built from source instead of using the prebuilt 1.1.1 version from CIPD.

The following prebuilt files are still used. They are build-time dependencies only and are not included in the APK:

- Chromium's Debian sysroot
- `ncursesw` used by bindgen
- Rust stage0
- `third_party/node/node_modules`

## Contributing

Each batch of work should have its own issue.

To contribute:

1. Pick an issue and claim the task.
2. Fork this repository.
3. Run the relevant workflows using your own GitHub Actions quota.
4. Submit a pull request with successful changes.

GitHub's free plan allows up to 20 concurrent jobs per account.

Contributions that successfully remove prebuilt dependencies, improve reproducibility, or bring the build closer to F-Droid's inclusion requirements are welcome.