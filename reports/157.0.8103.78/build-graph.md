## Flagged files and the chrome_public_apk build graph

167 scandelete rules cover 65855 flagged files that the build does not read.

| category | read by build | size | not read | size |
|---|---:|---:|---:|---:|
| test | 0 | 0 B | 62637 | 1.4 GB |
| other | 12 | 40.8 MB | 3218 | 9.1 GB |
| toolchain | 57 | 971.3 MB | 4581 | 4.5 GB |
| java | 195 | 79.2 MB | 165 | 98.3 MB |
| nonfree | 1 | 10.4 KB | 122 | 3.6 MB |

### Test/other files the build reads (need a decision)

| directory | count | size | kinds |
|---|---:|---:|---|
| `components/language` | 3 | 18.0 KB | binary 3 |
| `base/android` | 2 | 19.9 KB | DexClassLoader 2 |
| `(top level)` | 1 | 452 B | dependency file without lock 1 |
| `third_party/arcore-android-sdk-client/cipd` | 1 | 359.5 KB | Android AAR library 1 |
| `third_party/devtools-frontend/src` | 1 | 15.2 MB | binary 1 |
| `third_party/gperf/cipd` | 1 | 481.5 KB | binary 1 |
| `third_party/kotlin_stdlib/cipd` | 1 | 1.8 MB | Java JAR file 1 |
| `third_party/rust/chromium_crates_io` | 1 | 1.0 KB | binary 1 |
| `third_party/typescript/linux-amd64` | 1 | 23.0 MB | binary 1 |
