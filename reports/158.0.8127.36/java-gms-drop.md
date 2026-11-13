## Java compile: gms-drop (gms=drop)

- failed build steps: 11
- errors: 79 in 18 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `could not resolve Barcode` | 11 |
| `could not resolve Size` | 7 |
| `symbol not found com.google.android.gms.vision.barcode.Barcode` | 4 |
| `package com.google.android.gms.common.api` | 4 |
| `could not resolve Detector` | 3 |
| `could not resolve FirebaseApp` | 3 |
| `symbol ConnectionResult` | 3 |
| `could not resolve FusedLocationProviderClient` | 2 |
| `symbol not found com.google.android.gms.vision.Tracker` | 2 |
| `could not resolve Tracker` | 2 |
| `could not resolve InstanceID` | 2 |
| `could not resolve FirebaseInstallations` | 2 |
| `cannot access Task` | 2 |
| `symbol CommonStatusCodes` | 2 |
| `symbol ApiException` | 2 |
| `package com.google.android.gms.common` | 2 |
| `symbol GoogleApiAvailability` | 2 |
| `symbol not found com.google.android.gms.location.FusedLocationProviderClient` | 1 |
| `symbol not found com.google.android.gms.location.LocationCallback` | 1 |
| `could not resolve LocationCallback` | 1 |
| `symbol not found com.google.android.gms.vision.barcode.BarcodeDetector` | 1 |
| `could not resolve BarcodeDetector` | 1 |
| `symbol not found com.google.android.gms.vision.Frame` | 1 |
| `could not resolve Frame` | 1 |
| `symbol not found com.google.android.gms.vision.face.FaceDetector` | 1 |
| `could not resolve FaceDetector` | 1 |
| `symbol not found com.google.android.gms.vision.text.TextRecognizer` | 1 |
| `could not resolve TextRecognizer` | 1 |
| `symbol not found com.google.android.gms.vision.MultiProcessor` | 1 |
| `could not resolve MultiProcessor.Factory` | 1 |
| `symbol not found com.google.android.gms.common.images.Size` | 1 |
| `symbol not found com.google.android.gms.vision.Detector` | 1 |
| `symbol not found com.google.android.gms.iid.InstanceID` | 1 |
| `symbol not found com.google.firebase.FirebaseApp` | 1 |
| `symbol not found com.google.firebase.installations.FirebaseInstallations` | 1 |
| `symbol not found com.google.android.gms.cast.framework.OptionsProvider` | 1 |
| `could not resolve OptionsProvider` | 1 |
| `symbol not found com.google.android.gms.cast.framework.CastOptions` | 1 |
| `could not resolve CastOptions` | 1 |
| `symbol not found com.google.android.gms.cast.framework.SessionProvider` | 1 |
| `could not resolve SessionProvider` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `services/shape_detection/android` | 4 |
| `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode` | 3 |
| `services/device/geolocation/android` | 1 |
| `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk` | 1 |
| `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/camera` | 1 |
| `components/gcm_driver/instance_id/android` | 1 |
| `components/fcm/android` | 1 |
| `components/media_router/browser/android` | 1 |
| `chrome/browser/language/android` | 1 |
| `components/module_installer/android` | 1 |
| `components/one_time_tokens/android/backend/common` | 1 |
| `components/one_time_tokens/android/backend/sms` | 1 |
| `third_party/android_deps/util/org/chromium/gms` | 1 |

<details><summary>All files</summary>

- `chrome/browser/language/android/java/src/org/chromium/chrome/browser/language/LanguageSplitInstaller.java` (1)
- `components/fcm/android/java/src/org/chromium/components/fcm/FcmManager.java` (7)
- `components/gcm_driver/instance_id/android/java/src/org/chromium/components/gcm_driver/instance_id/InstanceIDWithSubtype.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastOptionsProvider.java` (6)
- `components/module_installer/android/java/src/org/chromium/components/module_installer/engine/SplitCompatEngine.java` (1)
- `components/one_time_tokens/android/backend/common/java/src/org/chromium/components/one_time_tokens/backend/OneTimeTokensMetricsRecorder.java` (4)
- `components/one_time_tokens/android/backend/sms/java/src/org/chromium/components/one_time_tokens/backend/sms/AndroidSmsOtpFetchReceiverBridge.java` (4)
- `services/device/geolocation/android/java/src/org/chromium/device/geolocation/LocationProviderGmsCore.java` (5)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/BarcodeDetectionImpl.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/BitmapUtils.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/FaceDetectionImplGmsCore.java` (2)
- `services/shape_detection/android/java/src/org/chromium/shape_detection/TextDetectionImpl.java` (2)
- `third_party/android_deps/util/org/chromium/gms/ChromiumPlayServicesAvailability.java` (7)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/QrCodeCaptureActivity.java` (2)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeContentProcessor.java` (5)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTracker.java` (6)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/QrCodeTrackerFactory.java` (8)
- `third_party/cardboard/src/sdk/qrcode/android/java/com/google/cardboard/sdk/qrcode/camera/CameraSource.java` (12)

</details>

### Failed steps

- `obj/services/device/geolocation/geolocation_java.turbine.jar`
- `obj/services/shape_detection/shape_detection_java.turbine.jar`
- `obj/third_party/cardboard/cardboard_java.turbine.jar`
- `obj/components/gcm_driver/instance_id/android/instance_id_driver_java.turbine.jar`
- `obj/components/fcm/android/fcm_java.turbine.jar`
- `obj/components/media_router/browser/android/cast_options_provider_java.turbine.jar`
- `obj/chrome/browser/language/android/base_module_java.javac.jar`
- `obj/components/module_installer/android/module_installer_java.javac.jar`
- `obj/components/one_time_tokens/android/backend/common/java.javac.jar`
- `obj/components/one_time_tokens/android/backend/sms/java.javac.jar`
- `obj/third_party/android_deps/chromium_play_services_availability_java.javac.jar`
