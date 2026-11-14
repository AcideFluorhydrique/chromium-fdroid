## Java compile: fdroid-genstubs (stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape,castoff,status)

- failed build steps: 4
- errors: 12 in 6 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `symbol not found com.google.android.gms.cast.framework.media.RemoteMediaClient$Callback` | 2 |
| `symbol Companion` | 2 |
| `symbol CreateCredentialException` | 2 |
| `symbol GetCredentialException` | 2 |
| `symbol not found com.google.android.gms.common.internal.GmsClient` | 1 |
| `could not resolve GmsClient` | 1 |
| `symbol not found com.google.android.gms.cast.Cast$Listener` | 1 |
| `CastOptions() has protected access in CastOptions` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `components/media_router/browser/android` | 3 |
| `chrome/browser/webid/android` | 2 |
| `components/webauthn/android` | 1 |

<details><summary>All files</summary>

- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsCreationDelegate.java` (3)
- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsPresentationDelegate.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/BaseSessionController.java` (2)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastOptionsProvider.java` (1)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastSessionController.java` (1)
- `components/webauthn/android/java/src/org/chromium/components/webauthn/Fido2ApiCall.java` (2)

</details>

### Failed steps

- `obj/components/webauthn/android/java.turbine.jar`
- `obj/components/media_router/browser/android/java.turbine.jar`
- `obj/chrome/browser/webid/java.javac.jar`
- `obj/components/media_router/browser/android/cast_options_provider_java.javac.jar`
