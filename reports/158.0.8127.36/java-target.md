## Java compile: target (gms=microg drop=playcore,mlkit,impress)

- failed build steps: 8
- errors: 61 in 12 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `could not resolve GenerativeModel` | 6 |
| `could not resolve SplitInstallStateUpdatedListener` | 4 |
| `could not resolve SplitInstallManager` | 4 |
| `could not resolve GenerativeModelFutures` | 4 |
| `could not resolve SplitInstallSessionStatus` | 3 |
| `could not resolve FirebaseApp` | 3 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallStateUpdatedListener` | 2 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallManager` | 2 |
| `symbol not found com.google.android.gms.vision.Tracker` | 2 |
| `could not resolve Tracker` | 2 |
| `could not resolve FirebaseInstallations` | 2 |
| `could not resolve InstanceID` | 2 |
| `symbol not found com.google.mlkit.genai.prompt.GenerativeModel` | 2 |
| `symbol not found com.google.mlkit.genai.prompt.java.GenerativeModelFutures` | 2 |
| `could not resolve FeatureStatus` | 2 |
| `symbol Builder` | 2 |
| `symbol not found com.google.android.gms.vision.face.FaceDetector` | 1 |
| `could not resolve FaceDetector` | 1 |
| `symbol not found com.google.android.gms.vision.text.TextRecognizer` | 1 |
| `could not resolve TextRecognizer` | 1 |
| `symbol not found com.google.android.play.core.splitinstall.SplitInstallRequest` | 1 |
| `could not resolve SplitInstallRequest` | 1 |
| `symbol not found com.google.android.play.core.splitinstall.model.SplitInstallSessionStatus` | 1 |
| `symbol not found com.google.android.gms.vision.MultiProcessor` | 1 |
| `could not resolve MultiProcessor.Factory` | 1 |
| `symbol not found com.google.firebase.FirebaseApp` | 1 |
| `symbol not found com.google.firebase.installations.FirebaseInstallations` | 1 |
| `symbol not found com.google.android.gms.iid.InstanceID` | 1 |
| `symbol not found com.google.mlkit.genai.common.FeatureStatus` | 1 |
| `symbol not found com.google.mlkit.genai.prompt.GenerateContentRequest` | 1 |
| `symbol not found com.google.mlkit.genai.common.GenAiException` | 1 |
| `could not resolve GenerateContentRequest` | 1 |
| `could not resolve GenAiException` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `services/shape_detection/android` | 2 |
| `components/module_installer/android` | 2 |
| `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode` | 2 |
| `services/on_device_model/android` | 2 |
| `chrome/browser/language/android` | 1 |
| `components/fcm/android` | 1 |
| `components/gcm_driver/instance_id/android` | 1 |
| `components/media_router/browser/android` | 1 |

<details><summary>All files</summary>

- `chrome/browser/language/android/java/src/org/chromium/chrome/browser/language/LanguageSplitInstaller.java` (9)
- `components/fcm/android/java/src/org/chromium/components/fcm/FcmManager.java` (7)
- `components/gcm_driver/instance_id/android/java/src/org/chromium/components/gcm_driver/instance_id/InstanceIDWithSubtype.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastOptionsProvider.java` (2)
- `components/module_installer/android/java/src/org/chromium/components/module_installer/engine/SplitCompatEngine.java` (3)
- `components/module_installer/android/java/src/org/chromium/components/module_installer/engine/SplitCompatEngineFacade.java` (6)
- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreModelDownloaderBackendImpl.java` (10)
- `services/on_device_model/android/java/src/org/chromium/on_device_model/MlKitAiCoreSessionBackendImpl.java` (11)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/FaceDetectionImplGmsCore.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/TextDetectionImpl.java` (2)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTracker.java` (2)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTrackerFactory.java` (4)

</details>

### Failed steps

- `obj/services/shape_detection/shape_detection_java.turbine.jar`
- `obj/components/module_installer/android/module_installer_java.turbine.jar`
- `obj/chrome/browser/language/android/base_module_java.turbine.jar`
- `obj/third_party/cardboard/cardboard_java.turbine.jar`
- `obj/components/fcm/android/fcm_java.turbine.jar`
- `obj/components/gcm_driver/instance_id/android/instance_id_driver_java.turbine.jar`
- `obj/services/on_device_model/android/java.turbine.jar`
- `obj/components/media_router/browser/android/cast_options_provider_java.javac.jar`
