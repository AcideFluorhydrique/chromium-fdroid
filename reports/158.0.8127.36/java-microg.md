## Java compile: microg (gms=microg)

- failed build steps: 5
- errors: 22 in 7 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `could not resolve FirebaseApp` | 3 |
| `symbol not found com.google.android.gms.vision.Tracker` | 2 |
| `could not resolve Tracker` | 2 |
| `could not resolve InstanceID` | 2 |
| `could not resolve FirebaseInstallations` | 2 |
| `symbol Builder` | 2 |
| `symbol not found com.google.android.gms.vision.face.FaceDetector` | 1 |
| `could not resolve FaceDetector` | 1 |
| `symbol not found com.google.android.gms.vision.text.TextRecognizer` | 1 |
| `could not resolve TextRecognizer` | 1 |
| `symbol not found com.google.android.gms.vision.MultiProcessor` | 1 |
| `could not resolve MultiProcessor.Factory` | 1 |
| `symbol not found com.google.android.gms.iid.InstanceID` | 1 |
| `symbol not found com.google.firebase.FirebaseApp` | 1 |
| `symbol not found com.google.firebase.installations.FirebaseInstallations` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `services/shape_detection/android` | 2 |
| `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode` | 2 |
| `components/gcm_driver/instance_id/android` | 1 |
| `components/fcm/android` | 1 |
| `components/media_router/browser/android` | 1 |

<details><summary>All files</summary>

- `components/fcm/android/java/src/org/chromium/components/fcm/FcmManager.java` (7)
- `components/gcm_driver/instance_id/android/java/src/org/chromium/components/gcm_driver/instance_id/InstanceIDWithSubtype.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastOptionsProvider.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/FaceDetectionImplGmsCore.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/TextDetectionImpl.java` (2)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTracker.java` (2)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTrackerFactory.java` (4)

</details>

### Failed steps

- `obj/services/shape_detection/shape_detection_java.turbine.jar`
- `obj/third_party/cardboard/cardboard_java.turbine.jar`
- `obj/components/gcm_driver/instance_id/android/instance_id_driver_java.turbine.jar`
- `obj/components/fcm/android/fcm_java.turbine.jar`
- `obj/components/media_router/browser/android/cast_options_provider_java.javac.jar`
