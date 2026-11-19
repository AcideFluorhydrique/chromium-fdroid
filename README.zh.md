[🇬🇧English](./README.md)  |  [🇹🇼中文](./README.zh.md)

---


# chromium-fdroid

讓 Chromium for Android 能照 [F-Droid 的收錄規則](https://f-droid.org/docs/Inclusion_Policy/) 從原始碼編譯。

## 目標

最終目標是和 F-Droid 社群一起，把 Chromium for Android 送進 F-Droid 的軟體庫，追蹤在 [fdroiddata#3911](https://gitlab.com/fdroid/fdroiddata/-/work_items/3911)。符合規則的 Chromium 編譯流程，也能成為之後收錄其他 Chromium 分支、以及其他 app 用到的元件（WebRTC、PDFium、Cronet）的基礎。

步驟：

1. **先在這裡測試（目前階段）**：在免費的 GitHub Actions runner 上，找出編譯流程的哪些部分能從原始碼編、或換成 F-Droid 接受的來源，並把所有東西都做成這個 repo 裡可以重跑的 workflow、腳本和報告。
2. **到 fdroiddata#3911 回報，和 F-Droid 討論做法**：分享結果，和維護者討論還沒定的問題：`scandelete`/`scanignore` 規則、Maven 上的 Java 套件怎麼處理、fdroidserver 需要支援什麼。
3. **找到足夠的算力**：目前完整編一次，在 4 核 16GB 的 runner 上，工具鏈約 2.5 小時、APK 約 12 小時，還要拆成每段 6 小時以內。F-Droid 是在自己的編譯伺服器上一次編完，所以要和 F-Droid 社群討論：有沒有更大的編譯資源、能不能用其他人提供的算力（例如 fdroiddata#3911 討論串裡有人主動提過），以及能不能透過可重現編譯（reproducible builds），讓 F-Droid 驗證在別處編出來的 APK。
4. **向 fdroiddata 提交 app 的 metadata。**

**這個 repo 不發布 APK。**平常用的 Chromium 在 [AcideFluorhydrique/chromium](https://github.com/AcideFluorhydrique/chromium) 發布。

## 怎麼跑

Actions → **Build Chromium Android for F-Droid tests** → Run workflow。

- `version`：Chromium 版本 tag，留空就用最新的 Android Stable。
- `own_toolchain`：clang / lld、rust / bindgen、gn、ninja、node 全部自己從原始碼編，不用 Google 預編譯的。
- `package_name`：預設 `org.chromium.chrome.fdroidtest`，可以和正式發布的版本同時安裝。
- `toolchain_from`：直接用之前 run 編好的工具鏈（`owner/repo/run_id`），可以填好幾個，用空白分隔，後面的優先。省掉約 2.5 小時。artifact 保留 7 天。
  158.0.8127.36 在 Debian 裡編的工具鏈（到 2026-11-21）：`AcideFluorhydrique/chromium-fdroid/43426073206 AcideFluorhydrique/chromium-fdroid/43573902951 AcideFluorhydrique/chromium-fdroid/43711783516`（gn/ninja/node 取第一個，rust 取第二個，對 Debian 系統編的 clang 取第三個）。
- `variant`：在 `gn gen` 前用 [`gms_variant.py`](.github/scripts/gms_variant.py) 換掉不自由的 Java 函式庫。完整的 F-Droid 組合是 `androidx=release stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs patch=cast,shape,castoff,status,fido,nogms`。再加上 `tools=r8,turbine` 會把 R8 和 turbine 也換成 Maven 上已發布的版本（測試中）。
- `gn_args`：接在 `args.gn` 最後的額外 GN 參數，實驗用（例如 `use_sysroot = false use_clang_modules = false`）。
- `resume_from`、`resume_out`、`fixup`：從另一個 run 的 `chromium-src` 和 `out/` artifact（保留 3 天）接著編，不用重頭來：分別是 run id、從哪個 `out/` artifact 開始（例如 `chromium-out-2`）、以及 ninja 之前用來修改 `src` 裡檔案的 shell 指令（可不填）。最後幾步（R8、打包）壞掉時，大約 3 小時就能修好重編。

release 編譯會設 `dcheck_always_on = false`；Chromium 對不是 official 的 release 編譯預設會開 DCHECK。

免費 runner 單一 job 最多 6 小時，所以分成幾段：

1. `toolchain.yml`：三個 job 並行，分別編 clang、rust、gn/ninja/node，約 2.5 小時。
2. `stage.yml`：照正式發布的接力方式編 APK，stage 1 會把 `gclient sync` 抓到的 Google 預編譯工具鏈換成第 1 步編好的，並在 job summary 列出兩邊的 hash 和版本。

## 目前進度

| 項目 | 狀態 |
|---|---|
| 工具鏈從原始碼編（clang、rust、gn、ninja、node） | 完成：用它編 `chrome_public_apk` 157.0.8103.50（[run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43129945973)，490MB）和 158.0.8127.36（[run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43386249559)，493MB）都成功 |
| 在 Debian（`debian:trixie`）裡編工具鏈，跟 F-Droid 編譯伺服器一樣 | 完成（[toolchain-debian.yml](.github/workflows/toolchain-debian.yml)）：用 Debian 的 clang 19 和 gcc 14、Debian `sdkmanager` 抓的 NDK、Debian 的 OpenSSL 3 和 ncursesw 編 rust、Debian `rustup` 裝的 Rust stage0。用它編完整 APK 的 run 正在跑 |
| 編譯會讀到的預編譯工具（tsc、esbuild、gperf、rollup 的 wasm） | 完成：全部在 Debian 裡從原始碼編（[tools-from-source.yml](.github/workflows/tools-from-source.yml)）；tsc 需要的 Go 1.26 也是從 Debian 的 Go 1.24 一路編上來 |
| `fdroid scanner` 掃描原始碼 | 157.0.8103.50、157.0.8103.78、158.0.8127.36 完成，見 [reports/](reports/) |
| 刪掉編譯不會讀到的被標記檔案（[#3](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/3)） | 完成：從編譯圖產生，照 fdroiddata#3911 的建議改成用腳本刪（[`fdroid/prune_binaries.py`](fdroid/prune_binaries.py)），70,988 筆降到約 5,000 筆 |
| 人工檢查編譯會讀到的檔案（[#7](https://github.com/AcideFluorhydrique/chromium-fdroid/issues/7)） | 完成：7 個放行（[`fdroid/scanignore.txt`](fdroid/scanignore.txt)），其他都換掉了（見上下兩列） |
| 不同步 APK 用不到的 DEPS | 完成：[`fdroid/skip-deps.txt`](fdroid/skip-deps.txt) 33 條，編譯需要的檔案都還在（[sync-trim.md](reports/158.0.8127.36/sync-trim.md)） |
| `third_party/android_deps` 和 `androidx` 的 Java 函式庫 | 編譯讀到的 197 個檔案全部和上游逐位元組相同：121 個和 Google Maven / Maven Central 一樣，76 個和 androidx.dev 的 CI 快照一樣（[maven-verify.md](reports/158.0.8127.36/maven-verify.md)）。把快照換成 Google Maven 上已發布的 androidx 版本後（fdroiddata#3911 已同意這個做法），Java 能編過（[java-androidx-release.md](reports/158.0.8127.36/java-androidx-release.md)），完整的 APK 也能編出來。有一個發布版的行為不一樣：slidingpanelayout 用 1.2.0 取代 1.3.0 快照（1.3.0 從來沒發布過）時，每個設定頁都會超出螢幕右邊；`androidx=release` 現在會自動修補 `MultiColumnSettings`（見[實機測試](#實機測試1580812736)） |
| 拿掉 Play 服務、Firebase、ML Kit、Play Core、ARCore | 編譯部分完成：全部換掉後能編出完整的 arm64 APK（[run](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/43816927601)，364MB）。microG 的 client 函式庫從 Maven Central 下載，版本和 sha256 固定在 [`fdroid/microg.lock`](fdroid/microg.lock)，它們的 ProGuard 規則也會交給 R8；microG 沒有的部分用只有簽名的 stub（fdroiddata#3911 已同意），以原始碼的形式放在 [`fdroid/stubs`](fdroid/stubs) 和 [`fdroid/stubs-gen`](fdroid/stubs-gen)（只有 Chromium 用到的類，由 [stubgen.yml](.github/workflows/stubgen.yml) 重新產生），所以編譯時不會下載任何 Google 的函式庫；ML Kit/ARCore/VR 用 GN 參數關掉，再加幾個小補丁。`patch=nogms` 讓 app 即使手機裝了 Play 服務，也當作沒有。在兩台有 Play 服務的手機，以及沒有 Play 服務、有 microG 的模擬器上測過：沒有連到 Play 服務，也沒有閃退（見[實機測試](#實機測試1580812736)）。passkey 不能用，帳號密碼登入可以。Discover 資訊流載不出來 |
| Android 編譯工具改用 `sdkmanager` / Maven 的版本（aapt2、bundletool、kotlinc、protoc 等） | 進行中：fdroiddata#3911 同意 R8 和 turbine 用 Maven 上已發布的版本，所以 R8 不用從原始碼編。`tools=r8,turbine`（[`build_tools_maven.py`](.github/scripts/build_tools_maven.py)）會把兩個都換掉、從原始碼重編 Chromium 的 `custom_d8.jar`/`custom_r8.jar`，並且不再使用那兩個 GraalVM 原生執行檔；用它編的 run 正在跑。aapt2 和 Google Maven 上的完全相同（[android-tools.md](reports/158.0.8127.36/android-tools.md)）。其他還沒開始 |
| 拿掉執行時對 Google 服務的連線（Safe Browsing、variations、元件更新、metrics、Discover 等） | 未開始：F-Droid 希望把這些用補丁拿掉，而不是只標成 NonFreeNet。第一步是先記錄全新安裝後實際連了哪些地方 |

## 實機測試（158.0.8127.36）

F-Droid 版（arm64，[run 44267270985](https://github.com/AcideFluorhydrique/chromium-fdroid/actions/runs/44267270985)：完整的 F-Droid 組合加上 `patch=nogms` 和 slidingpanelayout 的修正）透過 adb 在兩台手機上測試，用 `uiautomator` 操作，再用截圖、`dumpsys` 和 logcat 檢查：

- Motorola edge 2024，LineageOS（Android 16），Google 應用程式是使用者自己裝的
- REDMI Note 15，HyperOS 3（Android 16），bootloader 未解鎖（`verifiedbootstate=green`），原廠內建 Play 服務

| 測試 | 結果 |
|---|---|
| 設定頁版面（隱私和安全性、無障礙） | 已修好：卡片有右邊距和圓角，開關都看得到。右側面板寬 1080px，等於螢幕寬；修正前是 1338px |
| Reader mode（Wikipedia 文章，從選單打開） | 正常，文字和圖片都有。曾經在一台用 Rethink DNS 的手機上圖片空白：它把網域解析成 100.64.0.0/10 的位址，Chromium 把這些當成區域網路，不讓 Reader mode 頁面載入（`InsecureLocalNetwork`），不是這個版本特有的問題 |
| 文章下方的「簡化檢視」提示 | 不會出現。同一台手機上的原版 Chromium 158.0.8127.36 也一樣不會出現 |
| 首次啟動 | 沒有 Google 登入畫面 |
| Play 服務：Google Maps（含「現在地」）、Gemini、Google 登入頁、YouTube、Google 搜尋 | app 的程序沒有任何連到 `com.google.android.gms` 的服務連線。定位走 Android 的 `LocationManager`（這兩台手機上，系統的 fused 定位本身是由 Play 服務提供，任何 app 都一樣）。唯一相關的 log 是 Google 登入頁查詢 passkey 時的 `Fido2PrivilegedApi is not available` |
| 閃退 | 沒有 |

在 Android 35 模擬器裡（[emulator.yml](.github/workflows/emulator.yml)），含修正的 x64 版在有 Play 服務時設定頁版面正常，在純 AOSP（沒有任何 Google 服務）和 AOSP 加 microG 上都能啟動、瀏覽，沒有閃退；截圖在 [`emulator-results`](https://github.com/AcideFluorhydrique/chromium-fdroid/tree/emulator-results/runs) 分支。

設定頁 bug 的原因：SlidingPaneLayout 會把右側面板包在一個 `TouchBlocker` 裡。1.3.0 快照的 `TouchBlocker` 和面板共用同一份 `LayoutParams`；1.2.0 的則是有自己 `LayoutParams` 的 `FrameLayout`。`MultiColumnSettings` 把面板設成 480dp，讓 SlidingPaneLayout 決定要單欄還是雙欄，但在 1.2.0 這個寬度只設到了 `TouchBlocker` 裡面的面板，結果面板在螢幕寬的容器裡照樣畫成 480dp。修正改成把寬度設在 `TouchBlocker` 上。

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

- clang 沒做 bootstrap、PGO、ThinLTO、BOLT，所以 APK 編起來慢約 30%；起點是主機上的 clang（Ubuntu 的 clang-18 或 Debian 的 clang 19）。
- 沒編 Android riscv64 的 runtime；Debian 版也不編其他 CPU 的桌面 Linux runtime（APK 用不到）。
- crubit 只編 Chromium 用到的 `cc_bindings_from_rs`。
- gn 用 gcc 編（用到 C++23 的 `std::expected`，clang-18 配 Ubuntu 的 libstdc++ 用不了）。
- rust 用 Debian 的 OpenSSL 3（或從原始碼編的 3.5），不用 CIPD 上預編譯的 1.1.1。

還在用的預編譯檔（只在編譯時用到，不會進 APK）：

- Rust 的 stage0，用 Debian 的 `rustup` 從 static.rust-lang.org 安裝
- NDK，用 Debian 的 `sdkmanager` 安裝，並對照 F-Droid 的 transparency log 檢查

[toolchain-debian.yml](.github/workflows/toolchain-debian.yml) 的 `clang-hostsys` 讓 clang 自己的工具改對 Debian 系統編，不用 Chromium 的 amd64 sysroot（編出來的程式只需要 glibc 2.38，Ubuntu 24.04 上照樣能跑）；libxml2 和 zstd 改從 GNOME GitLab 和 GitHub 下載（和 Google 鏡像上的逐位元組相同）。現在完全不從 Google 的儲存空間下載東西。

## 一起幫忙

每個批次開一個 issue，認領後 fork 這個 repo，用自己帳號的 Actions 額度跑（免費帳號同時最多 20 個 job）。成功的改動開 PR 合回來。
