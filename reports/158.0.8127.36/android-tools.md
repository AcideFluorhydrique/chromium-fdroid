## Prebuilt Android build tools

24 CIPD packages; 15 have files the chrome_public_apk build graph reads (tools run by scripts may not show up as inputs).

| directory | CIPD version | build inputs | Maven |
|---|---|---:|---|
| `third_party/android_build_tools/aapt2/cipd` | `version:2@9.6.0-alpha03-16666295 version:2@9.6.0-alpha02-16666295 version:2@9.6.0-alpha01-16666295` | 1 | 9.6.0-alpha03-16666295 on Google Maven, identical |
| `third_party/android_build_tools/aapt2/linux-amd64` | `version:2@9.6.0-alpha03-16666295 version:2@9.6.0-alpha02-16666295 version:2@9.6.0-alpha01-16666295` | 0 |  |
| `third_party/android_build_tools/bazel_tools/cipd` | `version:2@7.4.1` | 1 |  |
| `third_party/android_build_tools/bundletool/cipd` | `version:2@1.18.3.f4d062e115 version:2@1.18.3.b5a36d3429 version:2@1.18.3.acec2b8ec9 version:2@1.18.3.df95ace3a6 version:2@1.18.3.8c7436a84b version:2@1.18.3.a8e182fbbb version:2@1.18.3.f7586895bf version:2@1.18.3.9b31b8a14c version:2@1.18.3.ebf059ba87 version:2@1.18.3.e13b23389c version:2@1.18.3.6e8e9e7cdc` | 0 | 1.18.3 on Google Maven, different; GitHub release bundletool-all identical |
| `third_party/android_build_tools/error_prone/cipd` | `version:2@2.51.0.b91c5b18c0` | 0 | 2.51.0 on Maven Central |
| `third_party/android_build_tools/error_prone_javac/cipd` | `version:2@9-dev-r4023-3.32a18f6164` | 0 |  |
| `third_party/android_build_tools/lint/cipd` | `version:2@32.5.0-alpha08.dbf279c9f2` | 0 | 32.5.0-alpha08 on Google Maven |
| `third_party/android_build_tools/manifest_merger/cipd` | `version:2@32.6.0-alpha01.30eab7e0dd` | 1 | 32.6.0-alpha01 on Google Maven, different, CIPD has 27116 entries, the other 128; 128 shared, 1 of them differ |
| `third_party/android_build_tools/nullaway/cipd` | `version:2@0.14.2.2be7cec8ac` | 0 | 0.14.2 on Maven Central |
| `third_party/android_build_tools/protoc/cipd` | `version:2@v35.1` | 1 |  |
| `third_party/android_build_tools/signflinger/cipd` | `version:2@9.5.0-alpha09.c0cf398784` | 2 | 9.5.0-alpha09 on Google Maven, different, CIPD has 330 entries, the other 6; 6 shared, 1 of them differ |
| `third_party/android_sdk/public` | `{android_sdk` | 3 |  |
| `third_party/android_sdk/public` | `version:23.0` | 3 |  |
| `third_party/android_sdk/public` | `version:31.2.10` | 3 |  |
| `third_party/android_sdk/public` | `{android_sdk` | 3 |  |
| `third_party/android_sdk/public` | `version:1.0.0` | 3 |  |
| `third_party/android_toolchain/ndk` | `version:2@30.0.16248370` | 3291 |  |
| `third_party/jdk/current` | `version:2@jdk-25.0.5+8.a4d27635bd.cr0` | 27 |  |
| `third_party/jdk/linux-amd64` | `version:2@jdk-25.0.5+8.a4d27635bd.cr0` | 0 |  |
| `third_party/jdk11` | `version:2@11.0.15+10.cr0` | 0 |  |
| `third_party/kotlinc/current` | `version:2@v2.4.21.04ddd66b2a` | 15 | 2.4.21 on Maven Central |
| `third_party/r8/cipd` | `version:2@83a62c553f64f2fe6d4ea65cce854433a38a5622.15a5c61e00` | 2 |  |
| `third_party/robolectric/cipd` | `version:2@android-all-17-robolectric-15733970-2921868143` | 0 |  |
| `third_party/turbine/cipd` | `version:2@7c3bd2472ddf244b9f0ad82c8e2fad9ab30d8988.6b1a716fda` | 1 |  |
