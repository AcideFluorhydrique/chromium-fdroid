## Java compile: target (gms=microg drop=playcore,mlkit,impress)

- failed build steps: 3
- errors: 39 in 5 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `could not resolve GenerativeModel` | 6 |
| `could not resolve SplitInstallStateUpdatedListener` | 4 |
| `could not resolve SplitInstallManager` | 4 |
| `could not resolve GenerativeModelFutures` | 4 |
| `could not resolve SplitInstallSessionStatus` | 3 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallStateUpdatedListener` | 2 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallManager` | 2 |
| `symbol not found com.google.mlkit.genai.prompt.GenerativeModel` | 2 |
| `symbol not found com.google.mlkit.genai.prompt.java.GenerativeModelFutures` | 2 |
| `could not resolve FeatureStatus` | 2 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallRequest` | 1 |
| `could not resolve SplitInstallRequest` | 1 |
| `symbol not found com.google.android.play.core.splitinstall.model.SplitInstallSessionStatus` | 1 |
| `symbol not found com.google.mlkit.genai.common.FeatureStatus` | 1 |
| `symbol not found com.google.mlkit.genai.prompt.GenerateContentRequest` | 1 |
| `symbol not found com.google.mlkit.genai.common.GenAiException` | 1 |
| `could not resolve GenerateContentRequest` | 1 |
| `could not resolve GenAiException` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `components/module_installer/android` | 2 |
| `services/on_device_model/android` | 2 |
| `chrome/browser/language/android` | 1 |

<details><summary>All files</summary>

- `chrome/browser/language/android/java/src/org/chromium/chrome/browser/language/LanguageSplitInstaller.java` (9)
- `components/module_installer/android/java/src/org/chromium/components/module_installer/engine/SplitCompatEngine.java` (3)
- `components/module_installer/android/java/src/org/chromium/components/module_installer/engine/SplitCompatEngineFacade.java` (6)
- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreModelDownloaderBackendImpl.java` (10)
- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreSessionBackendImpl.java` (11)

</details>

### Failed steps

- `obj/components/module_installer/android/module_installer_java.turbine.jar`
- `obj/chrome/browser/language/android/base_module_java.turbine.jar`
- `obj/services/on_device_model/android/java.turbine.jar`
