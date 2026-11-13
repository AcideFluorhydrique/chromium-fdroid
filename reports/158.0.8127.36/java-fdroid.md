## Java compile: fdroid (stubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape)

- failed build steps: 4
- errors: 37 in 8 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `package com.google.android.gms.identitycredentials` | 11 |
| `could not resolve MediaStatus` | 2 |
| `could not resolve RemoteMediaClient.Callback` | 2 |
| `symbol IdentityCredentialClient` | 2 |
| `package IdentityCredentialManager` | 2 |
| `symbol CreateCredentialRequest` | 2 |
| `symbol not found com.google.android.gms.common.internal.GmsClient` | 1 |
| `could not resolve GmsClient` | 1 |
| `symbol not found com.google.android.gms.identitycredentials.CreateCredentialHandle` | 1 |
| `symbol not found com.google.android.gms.identitycredentials.SignalCredentialStateRequest` | 1 |
| `symbol not found com.google.android.gms.identitycredentials.CreateCredentialRequest` | 1 |
| `could not resolve CreateCredentialHandle` | 1 |
| `could not resolve SignalCredentialStateRequest` | 1 |
| `could not resolve CreateCredentialRequest` | 1 |
| `symbol not found com.google.android.gms.cast.MediaStatus` | 1 |
| `symbol not found com.google.android.gms.cast.framework.media.RemoteMediaClient` | 1 |
| `could not resolve RemoteMediaClient` | 1 |
| `symbol not found com.google.android.gms.cast.framework.SessionManagerListener` | 1 |
| `could not resolve SessionManagerListener` | 1 |
| `symbol getConnectionResult()` | 1 |
| `symbol GetCredentialRequest` | 1 |
| `symbol CredentialOption` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `components/media_router/browser/android` | 3 |
| `components/webauthn/android` | 2 |
| `chrome/browser/webid/android` | 2 |
| `chrome/browser/password_manager/android` | 1 |

<details><summary>All files</summary>

- `chrome/browser/password_manager/android/java/src/org/chromium/chrome/browser/password_manager/PasswordManagerAndroidBackendUtil.java` (1)
- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsCreationDelegate.java` (9)
- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsPresentationDelegate.java` (10)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/MediaStatusBridge.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/BaseSessionController.java` (4)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CafBaseMediaRouteProvider.java` (2)
- `components/webauthn/android/java/src/org/chromium/components/webauthn/Fido2ApiCall.java` (2)
- `components/webauthn/android/java/src/org/chromium/components/webauthn/IdentityCredentialsHelper.java` (6)

</details>

### Failed steps

- `obj/components/webauthn/android/java.turbine.jar`
- `obj/components/media_router/browser/android/java.turbine.jar`
- `obj/chrome/browser/password_manager/android/java.javac.jar`
- `obj/chrome/browser/webid/java.javac.jar`
