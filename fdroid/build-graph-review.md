# Flagged files that chrome_public_apk reads

Issue #7. These are the files fdroid scanner flags in the "test" and "other"
categories that are inputs of the `chrome_public_apk` build graph
(`ninja -t inputs`), so the generated scandelete rules leave them alone.
Reviewed for Chromium 157.0.8103.50 and 157.0.8103.78.

## Accepted as source or data

Listed in [`scanignore.txt`](scanignore.txt).

| File | What it is | Decision |
|---|---|---|
| `base/android/java/src/org/chromium/base/BundleUtils.java`, `WrappedClassLoader.java` | Java source. Flagged for `DexClassLoader`, but `BaseDexClassLoader` is only used to call `findLibrary` for the app's own split APKs; no code is loaded | scanignore |
| `components/language/content/browser/ulp_language_code_locator/geolanguage-data_rank{0,1,2}.bin` | Serialized S2 quadtrees mapping locations to language codes, 3-10 KB each; copied in by `update_data.sh`. The CSV form of the same data is in `components/test/data/language/` | scanignore (data) |
| `package.json` | Declares no dependencies; only sets `"type": "module"` for the TypeScript compiler | scanignore |
| `third_party/rust/chromium_crates_io/vendor/jxl-v*/src/util/dither_32x32.bin` | 32x32 dither table loaded with `include_bytes!` by the `jxl` crate, part of its published crates.io source | scanignore (data) |

## Need to be replaced

| File | What it is | Replacement | Issue |
|---|---|---|---|
| `third_party/typescript/linux-amd64/src/lib/tsc` | TypeScript 7.0.2 native compiler (the Go port, typescript-go), used to compile WebUI TypeScript | Build typescript-go from source with Go at the pinned version | #8 |
| `third_party/devtools-frontend/src/third_party/esbuild/esbuild` | esbuild bundler (Go) used to build the DevTools frontend | Build esbuild from source with Go at the version devtools-frontend pins, or build without the DevTools frontend | #8 |
| `third_party/gperf/cipd/bin/gperf` | GNU gperf 3.2 (CIPD `3.2.chromium.1`), generates Blink's perfect hash tables | Debian's `gperf` package, or build GNU gperf 3.2 from source | #8 |
| `third_party/kotlin_stdlib/cipd/kotlin-stdlib-jdk8.jar` | Kotlin standard library | `org.jetbrains.kotlin:kotlin-stdlib-jdk8` from Maven Central | #5 |
| `third_party/arcore-android-sdk-client/cipd/core-1.44.0.aar` | ARCore client SDK, not free software | Build with `enable_arcore = false` | #6 |
