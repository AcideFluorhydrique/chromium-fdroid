## Prebuilt Java libraries in the chrome_public_apk build graph

| | android_deps | androidx |
|---|---:|---:|
| in build graph | 65 | 132 |
| exact version on Google Maven or Maven Central | 65 | 56 |
| not found (e.g. androidx snapshots) | 0 | 76 |
| non-free | 39 | 0 |

### Non-free artifacts and why they are in the build

- `com.google.android.gms:play-services-auth-api-phone:18.3.1`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/browser/ui/android/pdf/internal:java` → `//content/public/android:content_full_java` → `//third_party/android_deps:google_play_services_auth_api_phone_java` → `//third_party/android_deps:google_play_services_auth_api_phone_J__unpack_aar`
- `com.google.android.gms:play-services-auth-base:18.3.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//third_party/android_deps:google_play_services_auth_base_java` → `//third_party/android_deps:google_play_services_auth_base_J__unpack_aar`
- `com.google.android.gms:play-services-base:18.11.1`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_base_java` → `//third_party/android_deps:google_play_services_base_J__unpack_aar`
- `com.google.android.gms:play-services-basement:18.12.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_basement_java` → `//third_party/android_deps:google_play_services_basement_J__unpack_aar`
- `com.google.android.gms:play-services-cast:22.2.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//third_party/android_deps:google_play_services_cast_java` → `//third_party/android_deps:google_play_services_cast_J__unpack_aar`
- `com.google.android.gms:play-services-cast-framework:22.2.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//third_party/android_deps:google_play_services_cast_framework_java` → `//third_party/android_deps:google_play_services_cast_framework_J__unpack_aar`
- `com.google.android.gms:play-services-clearcut:17.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_vision_common_java` → `//third_party/android_deps:google_play_services_vision_common_java__classes` → `//third_party/android_deps:google_play_services_clearcut_java` → `//third_party/android_deps:google_play_services_clearcut_J__unpack_aar`
- `com.google.android.gms:play-services-cloud-messaging:17.4.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_play_services_cloud_messaging_java` → `//third_party/android_deps:google_play_services_cloud_messaging_J__unpack_aar`
- `com.google.android.gms:play-services-flags:18.1.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_vision_common_java` → `//third_party/android_deps:google_play_services_vision_common_java__classes` → `//third_party/android_deps:google_play_services_flags_java` → `//third_party/android_deps:google_play_services_flags_J__unpack_aar`
- `com.google.android.gms:play-services-gcm:17.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//third_party/android_deps:google_play_services_gcm_java` → `//third_party/android_deps:google_play_services_gcm_J__unpack_aar`
- `com.google.android.gms:play-services-identity-credentials:16.0.0-alpha12`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//chrome/browser/webid:java` → `//third_party/android_deps:google_play_services_identity_credentials_java` → `//third_party/android_deps:google_play_services_identity_credentials_J__unpack_aar`
- `com.google.android.gms:play-services-iid:17.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//third_party/android_deps:google_play_services_iid_java` → `//third_party/android_deps:google_play_services_iid_J__unpack_aar`
- `com.google.android.gms:play-services-location:21.4.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//chrome/browser/ui/android/omnibox:java` → `//third_party/android_deps:google_play_services_location_java` → `//third_party/android_deps:google_play_services_location_J__unpack_aar`
- `com.google.android.gms:play-services-phenotype:17.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_vision_common_java` → `//third_party/android_deps:google_play_services_vision_common_java__classes` → `//third_party/android_deps:google_play_services_phenotype_java` → `//third_party/android_deps:google_play_services_phenotype_J__unpack_aar`
- `com.google.android.gms:play-services-stats:17.0.2`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_play_services_stats_java` → `//third_party/android_deps:google_play_services_stats_J__unpack_aar`
- `com.google.android.gms:play-services-tasks:18.4.1`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//chrome/browser/language/android:base_module_java` → `//third_party/android_deps:google_play_services_tasks_java` → `//third_party/android_deps:google_play_services_tasks_J__unpack_aar`
- `com.google.android.gms:play-services-vision:20.1.3`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_vision_java` → `//third_party/android_deps:google_play_services_vision_J__unpack_aar`
- `com.google.android.gms:play-services-vision-common:19.1.3`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//services/shape_detection:shape_detection_java` → `//third_party/android_deps:google_play_services_vision_common_java` → `//third_party/android_deps:google_play_services_vision_common_J__unpack_aar`
- `com.google.android.play:app-update:2.1.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//chrome/browser/omaha/android:java` → `//third_party/android_deps:playcore_app_update_java` → `//third_party/android_deps:com_google_android_play_app_update_java` → `//third_party/android_deps:com_google_android_play_app_update_J__unpack_aar`
- `com.google.android.play:core-common:2.0.4`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:com_google_android_play_review_java` → `//third_party/android_deps:com_google_android_play_review_java__classes` → `//third_party/android_deps:com_google_android_play_core_common_java` → `//third_party/android_deps:com_google_android_play_core_common_J__unpack_aar`
- `com.google.android.play:feature-delivery:2.1.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:playcore_java` → `//third_party/android_deps:com_google_android_play_feature_delivery_java` → `//third_party/android_deps:com_google_android_play_feature_delivery_J__unpack_aar`
- `com.google.android.play:review:2.0.2`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:com_google_android_play_review_java` → `//third_party/android_deps:com_google_android_play_review_J__unpack_aar`
- `com.google.ar:impress:0.0.12`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//third_party/android_deps:com_google_ar_impress_java` → `//third_party/android_deps:com_google_ar_impress_J__unpack_aar`
- `com.google.firebase:firebase-annotations:18.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_common_java` → `//third_party/android_deps:google_firebase_firebase_common_java__classes` → `//third_party/android_deps:google_firebase_firebase_annotations_java` → `//third_party/android_deps:google_firebase_firebase_annotations_java__dex`
- `com.google.firebase:firebase-common:23.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_common_java` → `//third_party/android_deps:google_firebase_firebase_common_J__unpack_aar`
- `com.google.firebase:firebase-components:20.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_components_java` → `//third_party/android_deps:google_firebase_firebase_components_J__unpack_aar`
- `com.google.firebase:firebase-datatransport:21.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_datatransport_java` → `//third_party/android_deps:google_firebase_firebase_datatransport_J__unpack_aar`
- `com.google.firebase:firebase-encoders:18.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_encoders_java` → `//third_party/android_deps:google_firebase_firebase_encoders_java__dex`
- `com.google.firebase:firebase-encoders-json:19.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_encoders_json_java` → `//third_party/android_deps:google_firebase_firebase_encoders_json_J__unpack_aar`
- `com.google.firebase:firebase-encoders-proto:17.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_encoders_proto_java` → `//third_party/android_deps:google_firebase_firebase_encoders_proto_java__dex`
- `com.google.firebase:firebase-iid-interop:17.1.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_iid_interop_java` → `//third_party/android_deps:google_firebase_firebase_iid_interop_J__unpack_aar`
- `com.google.firebase:firebase-installations:20.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_installations_java` → `//third_party/android_deps:google_firebase_firebase_installations_J__unpack_aar`
- `com.google.firebase:firebase-installations-interop:18.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_installations_interop_java` → `//third_party/android_deps:google_firebase_firebase_installations_interop_J__unpack_aar`
- `com.google.firebase:firebase-measurement-connector:19.0.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java__classes` → `//third_party/android_deps:google_firebase_firebase_measurement_connector_java` → `//third_party/android_deps:google_firebase_firebase_measurement_connector_J__unpack_aar`
- `com.google.firebase:firebase-messaging:26.0.1`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:base_module_java` → `//third_party/android_deps:google_firebase_firebase_messaging_java` → `//third_party/android_deps:google_firebase_firebase_messaging_J__unpack_aar`
- `com.google.mlkit:common:18.11.0`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//services/on_device_model/android:java` → `//third_party/android_deps:mlkit_java` → `//third_party/android_deps:com_google_mlkit_common_java` → `//third_party/android_deps:com_google_mlkit_common_J__unpack_aar`
- `com.google.mlkit:genai-common:1.0.0-beta4`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//services/on_device_model/android:java` → `//third_party/android_deps:mlkit_java` → `//third_party/android_deps:com_google_mlkit_genai_common_java` → `//third_party/android_deps:com_google_mlkit_genai_common_J__unpack_aar`
- `com.google.mlkit:genai-prompt:1.0.0-beta4`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//services/on_device_model/android:java` → `//third_party/android_deps:mlkit_java` → `//third_party/android_deps:com_google_mlkit_genai_prompt_java` → `//third_party/android_deps:com_google_mlkit_genai_prompt_J__unpack_aar`
- `com.google.mlkit:genai-schema:1.0.0-alpha1`
  `//chrome/android:chrome_public_apk` → `//chrome/android:chrome_public_apk__java` → `//chrome/android:chrome_all_java` → `//chrome/android:chrome_java` → `//services/on_device_model/android:java` → `//third_party/android_deps:mlkit_java` → `//third_party/android_deps:com_google_mlkit_genai_prompt_java` → `//third_party/android_deps:com_google_mlkit_genai_prompt_java__classes` → `//third_party/android_deps:com_google_mlkit_genai_schema_java` → `//third_party/android_deps:com_google_mlkit_genai_schema_java__dex`

### Not found on Google Maven or Maven Central

| artifact | version |
|---|---|
| `androidx.activity:activity` | 1.14.0-SNAPSHOT |
| `androidx.activity:activity-compose` | 1.14.0-SNAPSHOT |
| `androidx.activity:activity-ktx` | 1.14.0-SNAPSHOT |
| `androidx.appsearch:appsearch` | 1.2.0-SNAPSHOT |
| `androidx.appsearch:appsearch-builtin-types` | 1.2.0-SNAPSHOT |
| `androidx.appsearch:appsearch-platform-storage` | 1.2.0-SNAPSHOT |
| `androidx.arch.core:core-common` | 2.3.0-SNAPSHOT |
| `androidx.arch.core:core-runtime` | 2.3.0-SNAPSHOT |
| `androidx.autofill:autofill` | 1.4.0-SNAPSHOT |
| `androidx.biometric:biometric` | 1.4.0-SNAPSHOT |
| `androidx.browser:browser` | 1.11.0-SNAPSHOT |
| `androidx.collection:collection-jvm` | 1.8.0-SNAPSHOT |
| `androidx.collection:collection-ktx` | 1.8.0-SNAPSHOT |
| `androidx.compose.animation:animation-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.animation:animation-core-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.foundation:foundation-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.foundation:foundation-layout-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.material3:material3-android` | 1.6.0-SNAPSHOT |
| `androidx.compose.material3:material3-ripple-android` | 1.6.0-SNAPSHOT |
| `androidx.compose.material:material-ripple-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.runtime:runtime-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.runtime:runtime-annotation-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.runtime:runtime-retain-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.runtime:runtime-saveable-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-geometry-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-graphics-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-text-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-unit-android` | 1.14.0-SNAPSHOT |
| `androidx.compose.ui:ui-util-android` | 1.14.0-SNAPSHOT |
| `androidx.concurrent:concurrent-futures` | 1.4.0-SNAPSHOT |
| `androidx.constraintlayout:constraintlayout` | 2.3.0-SNAPSHOT |
| `androidx.constraintlayout:constraintlayout-core` | 1.2.0-SNAPSHOT |
| `androidx.coordinatorlayout:coordinatorlayout` | 1.4.0-SNAPSHOT |
| `androidx.core:core` | 1.20.0-SNAPSHOT |
| `androidx.core:core-ktx` | 1.20.0-SNAPSHOT |
| `androidx.core:core-pip` | 1.0.0-SNAPSHOT |
| `androidx.core:core-viewtree` | 1.1.0-SNAPSHOT |
| `androidx.credentials:credentials` | 1.7.0-SNAPSHOT |
| `androidx.drawerlayout:drawerlayout` | 1.3.0-SNAPSHOT |
| `androidx.dynamicanimation:dynamicanimation` | 1.2.0-SNAPSHOT |
| `androidx.emoji2:emoji2` | 1.8.0-SNAPSHOT |
| `androidx.emoji2:emoji2-views-helper` | 1.8.0-SNAPSHOT |
| `androidx.exifinterface:exifinterface` | 1.5.0-SNAPSHOT |
| `androidx.fragment:fragment` | 1.10.0-SNAPSHOT |
| `androidx.fragment:fragment-ktx` | 1.10.0-SNAPSHOT |
| `androidx.graphics:graphics-shapes-android` | 1.2.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-common-java8` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-common-jvm` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-livedata-core` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-process` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-runtime-compose-android` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-runtime-ktx-android` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-viewmodel-android` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-viewmodel-ktx` | 2.12.0-SNAPSHOT |
| `androidx.lifecycle:lifecycle-viewmodel-savedstate-android` | 2.12.0-SNAPSHOT |
| `androidx.mediarouter:mediarouter` | 1.9.0-SNAPSHOT |
| `androidx.pdf:pdf-core` | 1.0.0-SNAPSHOT |
| `androidx.pdf:pdf-document-service` | 1.0.0-SNAPSHOT |
| `androidx.pdf:pdf-ink` | 1.0.0-SNAPSHOT |
| `androidx.pdf:pdf-viewer` | 1.0.0-SNAPSHOT |
| `androidx.pdf:pdf-viewer-fragment` | 1.0.0-SNAPSHOT |
| `androidx.preference:preference` | 1.3.0-SNAPSHOT |
| `androidx.recyclerview:recyclerview` | 1.5.0-SNAPSHOT |
| `androidx.resourceinspection:resourceinspection-annotation` | 1.1.0-SNAPSHOT |
| `androidx.savedstate:savedstate-android` | 1.6.0-SNAPSHOT |
| `androidx.savedstate:savedstate-compose-android` | 1.6.0-SNAPSHOT |
| `androidx.savedstate:savedstate-ktx` | 1.6.0-SNAPSHOT |
| `androidx.slidingpanelayout:slidingpanelayout` | 1.3.0-SNAPSHOT |
| `androidx.tracing:tracing-android` | 2.1.0-SNAPSHOT |
| `androidx.transition:transition` | 1.8.0-SNAPSHOT |
| `androidx.viewpager2:viewpager2` | 1.2.0-SNAPSHOT |
| `androidx.window.sidecar:sidecar` | 1.0.0-SNAPSHOT |
| `androidx.window:window` | 1.6.0-SNAPSHOT |
| `androidx.window:window-core-android` | 1.6.0-SNAPSHOT |
