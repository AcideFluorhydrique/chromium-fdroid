# chromium-fdroid

測試 Chromium for Android 能不能照 [F-Droid 的收錄規則](https://f-droid.org/docs/Inclusion_Policy/) 從原始碼編譯，結果回報到 [fdroiddata#3911](https://gitlab.com/fdroid/fdroiddata/-/work_items/3911)。

這裡只做試驗，不發布 APK。平常用的 Chromium 在 [AcideFluorhydrique/chromium](https://github.com/AcideFluorhydrique/chromium) 發布。

## 怎麼跑

Actions → **Build Chromium Android for F-Droid tests** → Run workflow。

- `version`：Chromium 版本 tag，留空就用最新的 Android Stable。
- `own_toolchain`：clang / lld、rust / bindgen、gn、ninja、node 全部自己從原始碼編，不用 Google 預編譯的。
- `package_name`：預設 `org.chromium.chrome.fdroidtest`，可以和正式發布的版本同時安裝。

免費 runner 單一 job 最多 6 小時，所以分成幾段：

1. `toolchain.yml`：三個 job 並行，分別編 clang、rust、gn/ninja/node，約 2.5 小時。
2. `stage.yml`：照正式發布的接力方式編 APK，stage 1 會把 `gclient sync` 抓到的 Google 預編譯工具鏈換成第 1 步編好的，並在 job summary 列出兩邊的 hash 和版本。

## 目前進度

| 項目 | 狀態 |
|---|---|
| 工具鏈從原始碼編（clang、rust、gn、ninja、node） | 測試中 |
| `fdroid scanner` 掃描原始碼，列出剩下的預編譯檔 | 未開始 |
| Android 編譯工具改用 `sdkmanager` / Maven 的版本（aapt2、bundletool、kotlinc、protoc 等），r8 從原始碼編 | 未開始 |
| `third_party/android_deps` 和 `androidx` 的 443 個 Maven 套件 | 未開始，可以分批 |
| 拿掉不開源的 Play 服務、Firebase、ML Kit、ARCore 等 | 未開始 |

## 和 Chromium 官方工具鏈的差異

- clang 沒做 bootstrap、PGO、ThinLTO、BOLT；起點是 Ubuntu 的 clang-18。
- 沒編 riscv64 的 Android runtime（runner 上的 NDK 還沒有 API 37）。
- rust 沒編 crubit；起點是 Rust 官方的 stage0。
- gn 用 gcc-13 編（用到 C++23 的 `std::expected`，clang-18 配 Ubuntu 的 libstdc++ 用不了）。
- rust 用的 OpenSSL 3.5 從原始碼編，不用 CIPD 上預編譯的 1.1.1。

還在用的預編譯檔（只在編譯時用到，不會進 APK）：Chromium 的 Debian sysroot、bindgen 用的 ncursesw、Rust 的 stage0、`third_party/node/node_modules`。

## 一起幫忙

每個批次開一個 issue，認領後 fork 這個 repo，用自己帳號的 Actions 額度跑（免費帳號同時最多 20 個 job）。成功的改動開 PR 合回來。
