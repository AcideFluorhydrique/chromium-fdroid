## Java compile: fdroid-genstubs (stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape,castoff,status)

- failed build steps: 1
- errors: 9 in 1 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `method does not override or implement a method from a supertype` | 5 |
| `symbol doRead(TaskApiCall<FidoClient,Result>)` | 1 |
| `symbol getService()` | 1 |
| `FidoClient is not abstract and does not override abstract method requiresSignIn() in Client` | 1 |
| `constructor GmsClient in class GmsClient<T> cannot be applied to given types;` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `components/webauthn/android` | 1 |

<details><summary>All files</summary>

- `components/webauthn/android/java/src/org/chromium/components/webauthn/Fido2ApiCall.java` (9)

</details>

### Failed steps

- `obj/components/webauthn/android/java.javac.jar`
