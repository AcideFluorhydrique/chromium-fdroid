## CIPD Java libraries vs Maven

197 files of 197 libraries that chrome_public_apk reads.

| result | files |
|---|---:|
| identical | 120 |
| same contents | 0 |
| different | 1 |
| snapshot, identical | 0 |
| snapshot, same contents | 0 |
| snapshot, different | 0 |
| not on Maven | 76 |

Snapshots are compared with https://androidx.dev/snapshots/builds/16718948/artifacts/repository; "release" is the newest version of that artifact on Google Maven.

### different

| artifact | version | file | release | detail |
|---|---|---|---|---|
| `com.google.guava:guava` | 33.7.2-jre | guava.jar |  | 831 changed, 36 only in CIPD, 68 only on Maven; e.g. ['META-INF/MANIFEST.MF', 'META-INF/maven/com.google.guava/guava/pom.properties', 'META-INF/maven/com.google.guava/guava/pom.xml'] |

### not on Maven

| artifact | version | file | release | detail |
|---|---|---|---|---|
| `androidx.activity:activity` | 1.14.0-SNAPSHOT | activity.aar | 1.13.0 |  |
| `androidx.activity:activity-compose` | 1.14.0-SNAPSHOT | activity-compose.aar | 1.13.0 |  |
| `androidx.activity:activity-ktx` | 1.14.0-SNAPSHOT | activity-ktx.aar | 1.13.0 |  |
| `androidx.appsearch:appsearch` | 1.2.0-SNAPSHOT | appsearch.aar | 1.1.0 |  |
| `androidx.appsearch:appsearch-builtin-types` | 1.2.0-SNAPSHOT | appsearch-builtin-types.aar | 1.1.0 |  |
| `androidx.appsearch:appsearch-platform-storage` | 1.2.0-SNAPSHOT | appsearch-platform-storage.aar | 1.1.0 |  |
| `androidx.arch.core:core-common` | 2.3.0-SNAPSHOT | core-common.jar | 2.2.0 |  |
| `androidx.arch.core:core-runtime` | 2.3.0-SNAPSHOT | core-runtime.aar | 2.2.0 |  |
| `androidx.autofill:autofill` | 1.4.0-SNAPSHOT | autofill.aar | 1.3.0 |  |
| `androidx.biometric:biometric` | 1.4.0-SNAPSHOT | biometric.aar | 1.1.0 |  |
| `androidx.browser:browser` | 1.11.0-SNAPSHOT | browser.aar | 1.10.0 |  |
| `androidx.collection:collection-jvm` | 1.8.0-SNAPSHOT | collection-jvm.jar | 1.7.0 |  |
| `androidx.collection:collection-ktx` | 1.8.0-SNAPSHOT | collection-ktx.jar | 1.7.0 |  |
| `androidx.compose.animation:animation-android` | 1.14.0-SNAPSHOT | animation-android.aar | 1.12.1 |  |
| `androidx.compose.animation:animation-core-android` | 1.14.0-SNAPSHOT | animation-core-android.aar | 1.12.1 |  |
| `androidx.compose.foundation:foundation-android` | 1.14.0-SNAPSHOT | foundation-android.aar | 1.12.1 |  |
| `androidx.compose.foundation:foundation-layout-android` | 1.14.0-SNAPSHOT | foundation-layout-android.aar | 1.12.1 |  |
| `androidx.compose.material3:material3-android` | 1.6.0-SNAPSHOT | material3-android.aar | 1.4.0 |  |
| `androidx.compose.material3:material3-ripple-android` | 1.6.0-SNAPSHOT | material3-ripple-android.aar | 1.5.0-rc01 (pre-release) |  |
| `androidx.compose.material:material-ripple-android` | 1.14.0-SNAPSHOT | material-ripple-android.aar | 1.12.1 |  |
| `androidx.compose.runtime:runtime-android` | 1.14.0-SNAPSHOT | runtime-android.aar | 1.12.1 |  |
| `androidx.compose.runtime:runtime-annotation-android` | 1.14.0-SNAPSHOT | runtime-annotation-android.aar | 1.12.1 |  |
| `androidx.compose.runtime:runtime-retain-android` | 1.14.0-SNAPSHOT | runtime-retain-android.aar | 1.12.1 |  |
| `androidx.compose.runtime:runtime-saveable-android` | 1.14.0-SNAPSHOT | runtime-saveable-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-android` | 1.14.0-SNAPSHOT | ui-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-geometry-android` | 1.14.0-SNAPSHOT | ui-geometry-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-graphics-android` | 1.14.0-SNAPSHOT | ui-graphics-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-text-android` | 1.14.0-SNAPSHOT | ui-text-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-unit-android` | 1.14.0-SNAPSHOT | ui-unit-android.aar | 1.12.1 |  |
| `androidx.compose.ui:ui-util-android` | 1.14.0-SNAPSHOT | ui-util-android.aar | 1.12.1 |  |
| `androidx.concurrent:concurrent-futures` | 1.4.0-SNAPSHOT | concurrent-futures.jar | 1.3.0 |  |
| `androidx.constraintlayout:constraintlayout` | 2.3.0-SNAPSHOT | constraintlayout.aar | 2.2.2 |  |
| `androidx.constraintlayout:constraintlayout-core` | 1.2.0-SNAPSHOT | constraintlayout-core.jar | 1.1.2 |  |
| `androidx.coordinatorlayout:coordinatorlayout` | 1.4.0-SNAPSHOT | coordinatorlayout.aar | 1.3.0 |  |
| `androidx.core:core` | 1.20.0-SNAPSHOT | core.aar | 1.19.1 |  |
| `androidx.core:core-ktx` | 1.20.0-SNAPSHOT | core-ktx.aar | 1.19.1 |  |
| `androidx.core:core-pip` | 1.0.0-SNAPSHOT | core-pip.aar | 1.0.0-alpha04 (pre-release) |  |
| `androidx.core:core-viewtree` | 1.1.0-SNAPSHOT | core-viewtree.aar | 1.0.0 |  |
| `androidx.credentials:credentials` | 1.7.0-SNAPSHOT | credentials.aar | 1.6.0 |  |
| `androidx.drawerlayout:drawerlayout` | 1.3.0-SNAPSHOT | drawerlayout.aar | 1.2.0 |  |
| `androidx.dynamicanimation:dynamicanimation` | 1.2.0-SNAPSHOT | dynamicanimation.aar | 1.1.0 |  |
| `androidx.emoji2:emoji2` | 1.8.0-SNAPSHOT | emoji2.aar | 1.7.0 |  |
| `androidx.emoji2:emoji2-views-helper` | 1.8.0-SNAPSHOT | emoji2-views-helper.aar | 1.7.0 |  |
| `androidx.exifinterface:exifinterface` | 1.5.0-SNAPSHOT | exifinterface.aar | 1.4.2 |  |
| `androidx.fragment:fragment` | 1.10.0-SNAPSHOT | fragment.aar | 1.9.1 |  |
| `androidx.fragment:fragment-ktx` | 1.10.0-SNAPSHOT | fragment-ktx.aar | 1.9.1 |  |
| `androidx.graphics:graphics-shapes-android` | 1.2.0-SNAPSHOT | graphics-shapes-android.aar | 1.1.0 |  |
| `androidx.lifecycle:lifecycle-common-java8` | 2.12.0-SNAPSHOT | lifecycle-common-java8.jar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-common-jvm` | 2.12.0-SNAPSHOT | lifecycle-common-jvm.jar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-livedata-core` | 2.12.0-SNAPSHOT | lifecycle-livedata-core.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-process` | 2.12.0-SNAPSHOT | lifecycle-process.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.12.0-SNAPSHOT | lifecycle-runtime-android.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-runtime-compose-android` | 2.12.0-SNAPSHOT | lifecycle-runtime-compose-android.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-runtime-ktx-android` | 2.12.0-SNAPSHOT | lifecycle-runtime-ktx-android.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-viewmodel-android` | 2.12.0-SNAPSHOT | lifecycle-viewmodel-android.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-viewmodel-ktx` | 2.12.0-SNAPSHOT | lifecycle-viewmodel-ktx.aar | 2.11.0 |  |
| `androidx.lifecycle:lifecycle-viewmodel-savedstate-android` | 2.12.0-SNAPSHOT | lifecycle-viewmodel-savedstate-android.aar | 2.11.0 |  |
| `androidx.mediarouter:mediarouter` | 1.9.0-SNAPSHOT | mediarouter.aar | 1.8.1 |  |
| `androidx.pdf:pdf-core` | 1.0.0-SNAPSHOT | pdf-core.aar | 1.0.0-beta01 (pre-release) |  |
| `androidx.pdf:pdf-document-service` | 1.0.0-SNAPSHOT | pdf-document-service.aar | 1.0.0-beta01 (pre-release) |  |
| `androidx.pdf:pdf-ink` | 1.0.0-SNAPSHOT | pdf-ink.aar | 1.0.0-beta01 (pre-release) |  |
| `androidx.pdf:pdf-viewer` | 1.0.0-SNAPSHOT | pdf-viewer.aar | 1.0.0-beta01 (pre-release) |  |
| `androidx.pdf:pdf-viewer-fragment` | 1.0.0-SNAPSHOT | pdf-viewer-fragment.aar | 1.0.0-beta01 (pre-release) |  |
| `androidx.preference:preference` | 1.3.0-SNAPSHOT | preference.aar | 1.2.1 |  |
| `androidx.recyclerview:recyclerview` | 1.5.0-SNAPSHOT | recyclerview.aar | 1.4.0 |  |
| `androidx.resourceinspection:resourceinspection-annotation` | 1.1.0-SNAPSHOT | resourceinspection-annotation.jar | 1.0.1 |  |
| `androidx.savedstate:savedstate-android` | 1.6.0-SNAPSHOT | savedstate-android.aar | 1.5.0 |  |
| `androidx.savedstate:savedstate-compose-android` | 1.6.0-SNAPSHOT | savedstate-compose-android.aar | 1.5.0 |  |
| `androidx.savedstate:savedstate-ktx` | 1.6.0-SNAPSHOT | savedstate-ktx.aar | 1.5.0 |  |
| `androidx.slidingpanelayout:slidingpanelayout` | 1.3.0-SNAPSHOT | slidingpanelayout.aar | 1.2.0 |  |
| `androidx.tracing:tracing-android` | 2.1.0-SNAPSHOT | tracing-android.aar | 2.0.5 |  |
| `androidx.transition:transition` | 1.8.0-SNAPSHOT | transition.aar | 1.7.2 |  |
| `androidx.viewpager2:viewpager2` | 1.2.0-SNAPSHOT | viewpager2.aar | 1.1.0 |  |
| `androidx.window.sidecar:sidecar` | 1.0.0-SNAPSHOT | sidecar.aar |  |  |
| `androidx.window:window` | 1.6.0-SNAPSHOT | window.aar | 1.5.1 |  |
| `androidx.window:window-core-android` | 1.6.0-SNAPSHOT | window-core-android.aar | 1.5.1 |  |
