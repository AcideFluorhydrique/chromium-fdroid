## Java compile: drop-mlkit (drop=mlkit)

- failed build steps: 1
- errors: 21 in 2 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `could not resolve GenerativeModel` | 6 |
| `could not resolve GenerativeModelFutures` | 4 |
| `symbol not found com.google.mlkit.genai.prompt.GenerativeModel` | 2 |
| `symbol not found com.google.mlkit.genai.prompt.java.GenerativeModelFutures` | 2 |
| `could not resolve FeatureStatus` | 2 |
| `symbol not found com.google.mlkit.genai.common.FeatureStatus` | 1 |
| `symbol not found com.google.mlkit.genai.prompt.GenerateContentRequest` | 1 |
| `symbol not found com.google.mlkit.genai.common.GenAiException` | 1 |
| `could not resolve GenerateContentRequest` | 1 |
| `could not resolve GenAiException` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `services/on_device_model/android` | 2 |

<details><summary>All files</summary>

- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreModelDownloaderBackendImpl.java` (10)
- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreSessionBackendImpl.java` (11)

</details>

### Failed steps

- `obj/services/on_device_model/android/java.turbine.jar`
