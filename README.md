[🇬🇧English](./README.md)  |  [🇹🇼中文](./README.zh.md)

---


# chromium-fdroid

Working towards building Chromium for Android from source in compliance with [F-Droid's Inclusion Policy](https://f-droid.org/docs/Inclusion_Policy/).

## Goal

The goal is to get Chromium for Android into the F-Droid repository, together with the F-Droid community, as tracked in [fdroiddata#3911](https://gitlab.com/fdroid/fdroiddata/-/work_items/3911). A policy-compliant Chromium build would also be a base for packaging Chromium-based forks and the components other apps use (WebRTC, PDFium, Cronet).

Plan:

1. **Test here first (current phase).** Work out, on free GitHub Actions runners, which parts of the build can be done from source or replaced with sources F-Droid accepts, and keep everything reproducible as workflows, scripts and reports in this repository.
2. **Report and agree on the approach on fdroiddata#3911.** Share the results and discuss the open questions with F-Droid maintainers: the `scandelete`/`scanignore` rules, how the Java libraries from Maven should be handled, and what fdroidserver would need to support.
3. **Find enough build capacity.** A full build currently needs about 2.5 hours for the toolchain plus about 12 hours for the APK on 4-core, 16 GB runners, split into 6-hour jobs. F-Droid builds an app in a single run on its own build server, so this needs to be discussed with the F-Droid community: whether larger build resources are available, whether offers of compute from others (such as in the fdroiddata#3911 thread) can be used, and whether reproducible builds could let F-Droid verify an APK built elsewhere.
4. **Submit the app metadata to fdroiddata.**

**This repository does not distribute APKs.** Regular Chromium builds are published at [AcideFluorhydrique/chromium](https://github.com/AcideFluorhydrique/chromium).

## Running a Build

Go to **Actions → Build Chromium Android for F-Droid tests → Run workflow**.

Workflow inputs:

- `version`: Chromium version tag. Leave empty to use the latest Android Stable release.
- `own_toolchain`: Build clang/lld, Rust/bindgen, GN, Ninja, and Node from source instead of using Google's prebuilt toolchains.
- `package_name`: Android package name. Defaults to `org.chromium.chrome.fdroidtest`, allowing the test build to be installed alongside the regular release.
- `toolchain_from`: Reuse a toolchain built by previous workflow runs, as `owner/repo/run_id`. Several runs can be given, separated by spaces; later ones take precedence. Saves approximately 2.5 hours. Artifacts are retained for 7 days.
  Debian-built toolchain for 158.0.8127.36 (until 2026-11-21): `AcideFluorhydrique/chromium-fdroid/43426073206 AcideFluorhydrique/chromium-fdroid/43573902951 AcideFluorhydrique/chromium-fdroid/43711783516` (GN/Ninja/Node from the first run, Rust from the second, clang built against the Debian system from the third).
- `variant`: Replace the non-free Java libraries with [`gms_variant.py`](.github/scripts/gms_variant.py) before `gn gen`. The full F-Droid combination is `androidx=release stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape,castoff,status,fido`. Adding `tools=r8,turbine` also replaces R8 and turbine with releases from Maven (being tested).
- `gn_args`: Extra GN args appended to `args.gn`, for experiments (for example `use_sysroot = false use_clang_modules = false`).
- `resume_from`, `resume_out`, `fixup`: Continue a build from another run's `chromium-src` and `out/` artifacts (kept for 3 days) instead of starting over: the run ID, the `out/` artifact to start from (for example `chromium-out-2`), and an optional shell command that edits files in `src` before ninja. A failure in the last steps (R8, packaging) can then be fixed in about 3 hours.

Release builds set `dcheck_always_on = false`; Chromium turns DCHECKs on by default in release builds that are not official.

GitHub Actions free runners have a maximum execution time of 6 hours per job, so the build is split into multiple workflows:

1. **`toolchain.yml`**: Three parallel jobs build clang, Rust, and GN/Ninja/Node respectively. Takes approximately 2.5 hours.
2. **`stage.yml`**: Builds the APK using the same staged build process as the regular release. During Stage 1, prebuilt toolchains downloaded by `gclient sync` are replaced with the source-built versions from the first workflow. The job summary reports the versions and hashes of both toolchains for verification.

## Current Progress

| Task | Status |
|---|---|
| Build toolchain from source (clang, Rust, GN, Ninja, Node) | Done. `chrome_public_apk` builds with it for 157.0.8103.50 ([run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43129945973), 490 MB) and 158.0.8127.36 ([run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43386249559), 493 MB). |
| Build the toolchain inside Debian (`debian:trixie`), as F-Droid's build server would | Done ([toolchain-debian.yml](.github/workflows/toolchain-debian.yml)). Debian's clang 19 and gcc 14 as host compilers, the NDK from Debian's `sdkmanager`, Debian's OpenSSL 3 and ncursesw for Rust, Rust's stage0 from Debian's `rustup`. A full APK build with it is running. |
| Prebuilt tools the build reads (tsc, esbuild, gperf, rollup's wasm) | Done. All built from source in Debian ([tools-from-source.yml](.github/workflows/tools-from-source.yml)); Go 1.26 for tsc is itself built from Debian's Go 1.24. |
| Scan source tree with `fdroid scanner` | Done for 157.0.8103.50, 157.0.8103.78 and 158.0.8127.36. See [reports/](reports/). |
| Remove flagged files the build does not read ([#3](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/3)) | Done. Generated from the build graph; [`fdroid/prune_binaries.py`](fdroid/prune_binaries.py) deletes them in a script, as suggested on fdroiddata#3911. 70,988 findings down to about 5,000. |
| Review the flagged files the build reads ([#7](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/7)) | Done. 7 accepted in [`fdroid/scanignore.txt`](fdroid/scanignore.txt), the rest replaced (see above and below). |
| Skip DEPS entries the APK does not need | Done. 33 entries in [`fdroid/skip-deps.txt`](fdroid/skip-deps.txt); every build input still exists ([sync-trim.md](reports/158.0.8127.36/sync-trim.md)). |
| Java libraries in `third_party/android_deps` and `androidx` | All 197 files the build reads are byte-identical to upstream: 121 to Google Maven / Maven Central, 76 to an androidx.dev CI snapshot ([maven-verify.md](reports/158.0.8127.36/maven-verify.md)). With the snapshots replaced by released androidx versions on Google Maven (accepted on fdroiddata#3911), the Java compiles ([java-androidx-release.md](reports/158.0.8127.36/java-androidx-release.md)) and a full APK builds. |
| Remove Google Play services, Firebase, ML Kit, Play Core and ARCore | Done for the build: a full arm64 APK builds with all of them replaced ([run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43816927601), 364 MB). microG's client libraries from Maven Central, pinned by version and sha256 in [`fdroid/microg.lock`](fdroid/microg.lock), with their ProGuard rules passed to R8; signature-only stubs for what microG lacks (accepted on fdroiddata#3911), committed as source in [`fdroid/stubs`](fdroid/stubs) and [`fdroid/stubs-gen`](fdroid/stubs-gen) (only the classes Chromium uses, regenerated by [stubgen.yml](.github/workflows/stubgen.yml)), so the build downloads none of Google's libraries; GN args for ML Kit/ARCore/VR, and small patches. The APK browses normally on a device with Play services, where `chrome://version` shows microG's library version. Not yet tested on a device with microG or with no Play services. The Discover feed does not load. |
| Android build tools from `sdkmanager` / Maven (aapt2, bundletool, kotlinc, protoc, ...) | In progress. Released versions of R8 and turbine from Maven are accepted on fdroiddata#3911, so R8 does not have to be built from source. `tools=r8,turbine` ([`build_tools_maven.py`](.github/scripts/build_tools_maven.py)) replaces both, rebuilds Chromium's `custom_d8.jar`/`custom_r8.jar` from their sources and stops using the two GraalVM native binaries; a build with it is running. aapt2 is identical to the one on Google Maven ([android-tools.md](reports/158.0.8127.36/android-tools.md)). The rest is not started. |
| Remove connections to Google services at runtime (Safe Browsing, variations, component updates, metrics, Discover, ...) | Not started. F-Droid asks for these to be patched out, not only declared as NonFreeNet. The first step is to record what a fresh install connects to. |

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

The source-built toolchain is not identical to Chromium's official toolchain:

- **Clang:** No bootstrap build, PGO, ThinLTO, or BOLT, so the APK builds about 30% slower. The starting point is the host clang (Ubuntu's clang-18 or Debian's clang 19).
- **Compiler runtimes:** Not built for Android RISC-V, and (in the Debian build) not for desktop Linux on other CPUs, which an APK does not use.
- **Rust:** Crubit builds only `cc_bindings_from_rs`, the part Chromium uses.
- **GN:** Built with GCC, because GN uses C++23's `std::expected`, which clang-18 with Ubuntu's libstdc++ does not support.
- **OpenSSL:** Debian's OpenSSL 3 (or 3.5 built from source) instead of the prebuilt 1.1.1 from CIPD.

Prebuilt files still used at build time (not included in the APK):

- Rust's stage0 compiler, installed with Debian's `rustup` from static.rust-lang.org
- The NDK, installed with Debian's `sdkmanager` and checked against F-Droid's transparency log

With `clang-hostsys` in [toolchain-debian.yml](.github/workflows/toolchain-debian.yml), clang's host tools are built against the Debian system instead of Chromium's amd64 sysroot (the binaries need glibc 2.38, so they still run on Ubuntu 24.04), and libxml2 and zstd come from GNOME GitLab and GitHub (byte-identical to Google's copies). Nothing is downloaded from Google's storage any more.

## Contributing

Each batch of work should have its own issue.

To contribute:

1. Pick an issue and claim the task.
2. Fork this repository.
3. Run the relevant workflows using your own GitHub Actions quota.
4. Submit a pull request with successful changes.

GitHub's free plan allows up to 20 concurrent jobs per account.

Contributions that successfully remove prebuilt dependencies, improve reproducibility, or bring the build closer to F-Droid's inclusion requirements are welcome.