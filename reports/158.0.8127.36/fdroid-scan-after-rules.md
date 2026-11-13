## fdroid scanner: 5033 findings (4909 problems reported)

0 scandelete rules applied, 0 files deleted; 5 scanignore rules applied, 7 files accepted.

| category | count | size |
|---|---:|---:|
| Non-free dependency references (Play services, Firebase, ML Kit, unknown Maven repos) | 123 | 3.6 MB |
| Prebuilt Java/Android libraries (androidx, android_deps) | 361 | 178.7 MB |
| Toolchains, SDKs and build tools | 4545 | 5.4 GB |
| Test, fuzzing, benchmark and example data | 0 | 0 B |
| Other | 4 | 39.0 MB |

### "Other" by directory (top 60 by count)

| directory | count | size | kinds |
|---|---:|---:|---|
| `third_party/arcore-android-sdk-client/cipd` | 1 | 359.5 KB | Android AAR library 1 |
| `third_party/devtools-frontend/src` | 1 | 15.2 MB | binary 1 |
| `third_party/gperf/cipd` | 1 | 481.5 KB | binary 1 |
| `third_party/typescript/linux-amd64` | 1 | 23.0 MB | binary 1 |

### By kind

| kind | count | size |
|---|---:|---:|
| shared library | 3742 | 1.7 GB |
| Java JAR file | 317 | 702.1 MB |
| binary | 261 | 2.5 GB |
| Android AAR library | 256 | 119.4 MB |
| static library | 192 | 348.0 MB |
| executable binary, possibly code | 122 | 170.6 MB |
| usual suspect '(?<!org.microg.gms:)play-services' | 50 | 1.4 MB |
| usual suspect 'com.google.android.gms(?!.(oss-licenses-plugin\|strict-version-matcher-plugin))' | 44 | 1.3 MB |
| gzip file archive | 8 | 62.1 MB |
| usual suspect 'com.google.mlkit' | 8 | 222.8 KB |
| usual suspect 'com(\.google)?\.firebase[.:](?!firebase-jobdispatcher\|geofire-java)' | 7 | 219.9 KB |
| ZIP file archive | 5 | 107.5 MB |
| dependency file without lock | 5 | 2.6 KB |
| usual suspect 'com.google.android.libraries(?!.mapsplatform.secrets-gradle-plugin)' | 2 | 72.6 KB |
| usual suspect 'com.google.android.play:app-update' | 2 | 72.6 KB |
| usual suspect 'com.google.android.play:feature-delivery' | 2 | 72.6 KB |
| usual suspect 'com.google.android.play:review' | 2 | 72.6 KB |
| usual suspect 'androidx.credentials:credentials-play-services-auth' | 2 | 66.2 KB |
| unknown maven repo 'https://androidx.dev/snapshots/builds/16718948/artifacts/repository' | 2 | 66.2 KB |
| WebAssembly binary file | 2 | 1.4 MB |
| unknown maven repo 'https://jcenter.bintray.com' | 1 | 11.4 KB |
| unknown maven repo 'http://oss.sonatype.org/content/repositories/snapshots' | 1 | 3.8 KB |

### All findings by directory (top 60 by count)

| directory | count | size | kinds |
|---|---:|---:|---|
| `build/linux` | 1920 | 95.4 MB | shared library 1906, static library 6, gzip file archive 6 |
| `third_party/android_toolchain/ndk` | 1778 | 922.0 MB | shared library 1631, static library 119, binary 27 |
| `third_party/android_sdk/public` | 407 | 1.0 GB | Java JAR file 140, executable binary, possibly code 118, shared library 92 |
| `third_party/androidx/cipd` | 217 | 90.9 MB | Android AAR library 196, Java JAR file 16, usual suspect '(?<!org.microg.gms:)play-services' 2 |
| `third_party/android_deps/cipd` | 195 | 89.5 MB | Java JAR file 88, Android AAR library 59, usual suspect '(?<!org.microg.gms:)play-services' 19 |
| `third_party/llvm-build/Release+Asserts` | 89 | 397.4 MB | static library 61, binary 15, shared library 13 |
| `third_party/jdk/current` | 77 | 257.8 MB | shared library 40, binary 34, executable binary, possibly code 1 |
| `third_party/jdk11/current` | 77 | 221.8 MB | shared library 38, binary 37, Java JAR file 1 |
| `third_party/depot_tools/.cipd_bin` | 64 | 773.3 MB | binary 62, executable binary, possibly code 2 |
| `third_party/kotlinc/current` | 55 | 188.0 MB | Java JAR file 54, binary 1 |
| `third_party/android_deps` | 46 | 1.6 MB | usual suspect 'com.google.android.gms(?!.(oss-licenses-plugin\|strict-version-matcher-plugin))' 18, usual suspect '(?<!org.microg.gms:)play-services' 18, usual suspect 'com.google.mlkit' 3 |
| `third_party/rust-toolchain/lib` | 30 | 628.0 MB | shared library 21, dependency file without lock 5, static library 2 |
| `third_party/rust-toolchain/bin` | 11 | 244.3 MB | binary 11 |
| `third_party/arcore-android-sdk/src` | 10 | 20.5 KB | usual suspect '(?<!org.microg.gms:)play-services' 4, usual suspect 'com.google.android.gms(?!.(oss-licenses-plugin\|strict-version-matcher-plugin))' 3, usual suspect 'com.google.mlkit' 2 |
| `third_party/cardboard/src` | 6 | 17.1 KB | usual suspect 'com.google.android.gms(?!.(oss-licenses-plugin\|strict-version-matcher-plugin))' 3, usual suspect '(?<!org.microg.gms:)play-services' 3 |
| `third_party/androidx` | 4 | 132.4 KB | usual suspect '(?<!org.microg.gms:)play-services' 2, usual suspect 'androidx.credentials:credentials-play-services-auth' 1, unknown maven repo 'https://androidx.dev/snapshots/builds/16718948/artifacts/repository' 1 |
| `third_party/libaddressinput/src` | 4 | 4.6 KB | usual suspect 'com.google.android.gms(?!.(oss-licenses-plugin\|strict-version-matcher-plugin))' 2, usual suspect '(?<!org.microg.gms:)play-services' 2 |
| `buildtools/android` | 3 | 6.3 MB | Java JAR file 2, binary 1 |
| `third_party/android_build_tools/bazel_tools` | 3 | 514.5 KB | binary 3 |
| `third_party/r8/cipd` | 3 | 76.0 MB | Java JAR file 2, binary 1 |
| `third_party/android_build_tools/signflinger` | 2 | 18.9 MB | binary 1, Java JAR file 1 |
| `third_party/android_system_sdk/cipd` | 2 | 52.2 MB | Java JAR file 2 |
| `third_party/node/linux` | 2 | 166.6 MB | gzip file archive 1, binary 1 |
| `third_party/node/node_modules` | 2 | 12.3 MB | WebAssembly binary file 1, gzip file archive 1 |
| `third_party/r8` | 2 | 49.6 KB | Java JAR file 2 |
| `third_party/turbine/cipd` | 2 | 24.9 MB | binary 1, Java JAR file 1 |
| `buildtools/linux64-format` | 1 | 3.6 MB | binary 1 |
| `buildtools/linux64` | 1 | 8.8 MB | binary 1 |
| `buildtools/third_party` | 1 | 40.6 MB | binary 1 |
| `third_party/android_build_tools/aapt2` | 1 | 6.2 MB | binary 1 |
| `third_party/android_build_tools/bundletool` | 1 | 31.0 MB | Java JAR file 1 |
| `third_party/android_build_tools/error_prone` | 1 | 16.8 MB | Java JAR file 1 |
| `third_party/android_build_tools/error_prone_javac` | 1 | 2.7 MB | Java JAR file 1 |
| `third_party/android_build_tools/lint` | 1 | 132.4 MB | Java JAR file 1 |
| `third_party/android_build_tools/manifest_merger` | 1 | 44.1 MB | Java JAR file 1 |
| `third_party/android_build_tools/nullaway` | 1 | 5.9 MB | Java JAR file 1 |
| `third_party/android_build_tools/protoc` | 1 | 10.0 MB | binary 1 |
| `third_party/aosp_dalvik/cipd` | 1 | 912.4 KB | Java JAR file 1 |
| `third_party/arcore-android-sdk-client/cipd` | 1 | 359.5 KB | Android AAR library 1 |
| `third_party/depot_tools` | 1 | 25.2 MB | binary 1 |
| `third_party/devtools-frontend/src` | 1 | 15.2 MB | binary 1 |
| `third_party/gperf/cipd` | 1 | 481.5 KB | binary 1 |
| `third_party/libwebp/src` | 1 | 11.4 KB | unknown maven repo 'https://jcenter.bintray.com' 1 |
| `third_party/llvm-libclang/lib` | 1 | 103.7 MB | shared library 1 |
| `third_party/ninja` | 1 | 406.7 KB | binary 1 |
| `third_party/rust-toolchain/libexec` | 1 | 2.0 MB | binary 1 |
| `third_party/tflite/src` | 1 | 3.8 KB | unknown maven repo 'http://oss.sonatype.org/content/repositories/snapshots' 1 |
| `third_party/typescript/linux-amd64` | 1 | 23.0 MB | binary 1 |
