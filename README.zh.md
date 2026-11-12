# chromium-fdroid

測試 Chromium for Android 能不能照 [F-Droid 的收錄規則](https://f-droid.org/docs/Inclusion_Policy/) 從原始碼編譯，結果回報到 [fdroiddata#3911](https://gitlab.com/fdroid/fdroiddata/-/work_items/3911)。

這裡只做試驗，不發布 APK。平常用的 Chromium 在 [AcideFluorhydrique/chromium](https://github.com/AcideFluorhydrique/chromium) 發布。

## 怎麼跑

Actions → **Build Chromium Android for F-Droid tests** → Run workflow。

- `version`：Chromium 版本 tag，留空就用最新的 Android Stable。
- `own_toolchain`：clang / lld、rust / bindgen、gn、ninja、node 全部自己從原始碼編，不用 Google 預編譯的。
- `package_name`：預設 `org.chromium.chrome.fdroidtest`，可以和正式發布的版本同時安裝。
- `toolchain_from`：直接用之前 run 編好的工具鏈（`owner/repo/run_id`），可以填好幾個，用空白分隔，後面的優先。省掉約 2.5 小時。artifact 保留 7 天。
  157.0.8103.50 目前完整的工具鏈（到 2026-11-18）：`AcideFluorhydrique/chromium/43082253964 AcideFluorhydrique/chromium-fdroid/43129945973`（clang 和 tools 取第一個，含 crubit 的 rust 取第二個）。

免費 runner 單一 job 最多 6 小時，所以分成幾段：

1. `toolchain.yml`：三個 job 並行，分別編 clang、rust、gn/ninja/node，約 2.5 小時。
2. `stage.yml`：照正式發布的接力方式編 APK，stage 1 會把 `gclient sync` 抓到的 Google 預編譯工具鏈換成第 1 步編好的，並在 job summary 列出兩邊的 hash 和版本。

## 目前進度

| 項目 | 狀態 |
|---|---|
| 工具鏈從原始碼編（clang、rust、gn、ninja、node） | 都編得出來（clang 1h42m、rust 2h25m、gn/ninja/node 2h）；用它們編 APK 測試中 |
| `fdroid scanner` 掃描原始碼，列出剩下的預編譯檔 | 157 版完成，見 [reports/157.0.8103.50](reports/157.0.8103.50/fdroid-scan.md) |
| 用編譯圖產生 `scandelete` 規則（[#3](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/3)） | 167 條規則，套用後 70,988 筆降到 5,275 筆，見 [build-graph.md](reports/157.0.8103.50/build-graph.md)、[scan-rules.txt](reports/157.0.8103.50/scan-rules.txt) |
| 人工檢查編譯會讀到的檔案（[#7](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/7)） | 完成：7 個放行（[`fdroid/scanignore.txt`](fdroid/scanignore.txt)），5 個要換掉，已分派到 #5、#6、#8（[`fdroid/build-graph-review.md`](fdroid/build-graph-review.md)） |
| Android 編譯工具改用 `sdkmanager` / Maven 的版本（aapt2、bundletool、kotlinc、protoc 等），r8 從原始碼編 | 未開始 |
| `third_party/android_deps` 和 `androidx` 的 443 個 Maven 套件 | 未開始，可以分批 |
| 拿掉不開源的 Play 服務、Firebase、ML Kit、ARCore 等 | 未開始 |

## 掃描結果（157.0.8103.50）

`gclient sync` 完的原始碼被標記了 70,988 個檔案，大部分不會進 APK：

| 類別 | 數量 | 大小 | 處理方式 |
|---|---:|---:|---|
| 測試、fuzz、benchmark 資料 | 62,637 | 1.4 GB | 用 F-Droid metadata 的 `scandelete` 按目錄刪掉 |
| 工具鏈、SDK、編譯工具 | 4,638 | 5.4 GB | 工具鏈自己編；SDK/NDK/JDK 改用 `sdkmanager` 和 Debian 的版本 |
| 其他：只在測試或開發時用到的工具（robolectric、espresso、CTS、apache、cpython3、luci-go 等） | 161 | 8.1 GB | 不同步或刪掉 |
| 其他：小於 64KB 的資料檔（電話號碼資料、測試向量等） | 2,728 | 4.7 MB | 逐一確認後 `scanignore` |
| 其他：較大的檔案（devtools-frontend、openscreen、dawn、angle 等） | 341 | 1.2 GB | 要逐一看 |
| Java 套件（androidx、android_deps） | 360 | 178 MB | 改從 Maven 拿，或從原始碼編 |
| 不開源依賴的引用（Play 服務、Firebase、ML Kit、未知 Maven repo） | 123 | 3.6 MB | 打補丁拿掉 |

完整清單：[`fdroid-scan-findings.tsv.gz`](reports/157.0.8103.50/fdroid-scan-findings.tsv.gz)（欄位：類別、種類、路徑、大小、編譯是否會讀到）。

### 套用 scandelete 和 scanignore 規則之後

`scan.yml` 先用 `ninja -t inputs chrome_public_apk` 列出編 APK 會讀到的檔案。被標記、但編譯不會讀到的檔案，自動合併成 [167 條 `scandelete` 規則](reports/157.0.8103.50/scan-rules.txt)；套用後再掃一次：

| 類別 | 套用前 | 套用後 |
|---|---:|---:|
| 測試、fuzz、benchmark 資料 | 62,637 | 135（都是 `executable binary, possibly code` 警告，不會擋編譯） |
| 其他 | 3,230 | 12（7 個是警告；5 個是編譯需要、要換掉的工具和套件，見 [build-graph-review.md](fdroid/build-graph-review.md)） |
| 工具鏈、SDK、編譯工具 | 4,638 | 4,638 |
| Java 套件 | 360 | 360（其中 165 個 chrome_public_apk 根本用不到） |
| 不開源依賴的引用 | 123 | 123 |

注意：`ninja -t inputs` 只列出 GN 裡宣告過的輸入。工具鏈這一類被腳本直接呼叫的執行檔不一定會出現，所以這個判斷只用在測試資料和「其他」。

## 和 Chromium 官方工具鏈的差異

- clang 沒做 bootstrap、PGO、ThinLTO、BOLT；起點是 Ubuntu 的 clang-18。
- 沒編 riscv64 的 Android runtime（runner 上的 NDK 還沒有 API 37）。
- rust 沒編 crubit；起點是 Rust 官方的 stage0。
- gn 用 gcc-13 編（用到 C++23 的 `std::expected`，clang-18 配 Ubuntu 的 libstdc++ 用不了）。
- rust 用的 OpenSSL 3.5 從原始碼編，不用 CIPD 上預編譯的 1.1.1。

還在用的預編譯檔（只在編譯時用到，不會進 APK）：Chromium 的 Debian sysroot、bindgen 用的 ncursesw、Rust 的 stage0、`third_party/node/node_modules`。

## 一起幫忙

每個批次開一個 issue，認領後 fork 這個 repo，用自己帳號的 Actions 額度跑（免費帳號同時最多 20 個 job）。成功的改動開 PR 合回來。
