## Java compile: androidx-release (androidx=release)

- failed build steps: 2
- errors: 7 in 3 files (javac stops after 100 errors per target, so this is a lower bound)

### Missing packages and symbols

| what | errors |
|---|---:|
| `symbol Account` | 3 |
| `symbol setSource(String)` | 1 |
| `package Account` | 1 |
| `symbol fromDocumentClass(Class<WebPage>)` | 1 |
| `symbol EXTRA_CONTEXT_PAGE_TITLE` | 1 |

### Files with errors, by directory

| directory | files |
|---|---:|
| `chrome/browser/auxiliary_search` | 2 |
| `chrome/android` | 1 |

<details><summary>All files</summary>

- `chrome/android/java/src/org/chromium/chrome/browser/contextmenu/ChromeContextMenuPopulator.java` (1)
- `chrome/browser/auxiliary_search/java/src/org/chromium/chrome/browser/auxiliary_search/AuxiliarySearchDonationServiceBridge.java` (5)
- `chrome/browser/auxiliary_search/java/src/org/chromium/chrome/browser/auxiliary_search/AuxiliarySearchDonor.java` (1)

</details>

### Failed steps

- `obj/chrome/browser/auxiliary_search/java.javac.jar`
- `obj/chrome/android/chrome_java.javac.jar`
