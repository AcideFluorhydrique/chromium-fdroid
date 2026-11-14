## Java compile: fdroid-genstubs (stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape,castoff,status)

- failed build steps: 3
- errors: 32 in 10 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `method does not override or implement a method from a supertype` | 5 |
| `non-static method getClient(Activity) cannot be referenced from a static context` | 2 |
| `symbol CreateCredentialException` | 2 |
| `symbol GetCredentialException` | 2 |
| `symbol play()` | 2 |
| `symbol pause()` | 2 |
| `symbol setMessageReceivedCallbacks(String,this::onMe[...]eived)` | 2 |
| `non-static method getClient(Context) cannot be referenced from a static context` | 2 |
| `symbol registerCallback(Callback)` | 1 |
| `symbol unregisterCallback(Callback)` | 1 |
| `symbol requestStatus()` | 1 |
| `symbol addCastListener(CastSessionController.CastListener)` | 1 |
| `symbol removeCastListener(CastSessionController.CastListener)` | 1 |
| `symbol setContentType(String)` | 1 |
| `symbol load(MediaInfo,boolean,long)` | 1 |
| `symbol setStreamMute(boolean)` | 1 |
| `symbol setStreamVolume(double)` | 1 |
| `symbol seek(long)` | 1 |
| `symbol <FidoClient,Result>builder()` | 1 |
| `FidoClient is not abstract and does not override abstract method requiresSignIn() in Client` | 1 |
| `constructor GmsClient in class GmsClient<T> cannot be applied to given types;` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `components/media_router/browser/android` | 6 |
| `chrome/browser/webid/android` | 2 |
| `components/webauthn/android` | 2 |

<details><summary>All files</summary>

- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsCreationDelegate.java` (3)
- `chrome/browser/webid/android/java/src/org/chromium/chrome/browser/webid/DigitalCredentialsPresentationDelegate.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/BaseNotificationController.java` (2)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/BaseSessionController.java` (2)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CafMediaRouteProvider.java` (1)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastSessionController.java` (3)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/remoting/FlingingControllerAdapter.java` (7)
- `components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/remoting/RemotingSessionController.java` (1)
- `components/webauthn/android/java/src/org/chromium/components/webauthn/Fido2ApiCall.java` (8)
- `components/webauthn/android/java/src/org/chromium/components/webauthn/IdentityCredentialsHelper.java` (2)

</details>

### Failed steps

- `obj/chrome/browser/webid/java.javac.jar`
- `obj/components/media_router/browser/android/java.javac.jar`
- `obj/components/webauthn/android/java.javac.jar`
