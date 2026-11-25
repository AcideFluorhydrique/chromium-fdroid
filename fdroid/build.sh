#!/bin/bash
# Build Chromium for F-Droid: the steps of the GitHub Actions "all-in" build
# (build.yml with fdroid_tree, own toolchain, tools_from and the variant), in
# one script for an fdroiddata recipe, like Fennec's prebuild.sh / build.sh.
#
# Usage, from the root of this repository (fdroidserver's build directory):
#   fdroid/build.sh prebuild <chromium version> <cpu>
#   fdroid/build.sh build    <chromium version> <cpu>
# <cpu> is arm, arm64 or x64. Writes fdroid-out/ChromePublic-unsigned.apk.
#
# prebuild only fetches and trims the source (fdroidserver scans the tree
# after it); build compiles the toolchain and the tools from source, swaps in
# the Java libraries and build tools from Maven, and builds the APK, the way
# Fennec's build step builds LLVM and lets Gradle download from Maven.
#
# Environment:
#   ANDROID_NDK   NDK directory (fdroidserver's $$NDK$$, from the recipe's ndk:)
#   DEPOT_TOOLS   depot_tools checkout (fdroidserver's $$depot_tools$$ srclib);
#                 cloned when unset
#   PACKAGE_NAME  application id (default org.chromium.chrome.fdroid)
#   JOBS          parallel jobs (default: nproc)
#   JAVA_HOME     JDK to use instead of the CIPD one (not tried yet)
# For testing the script on GitHub Actions (6-hour jobs) only:
#   TOOLCHAIN_PKG directory with toolchain artifacts (*.tar.zst) of earlier
#                 toolchain builds, used instead of building the toolchain here
#   TOOLS_PKG     directory with the tools-from-source artifacts, likewise
#   NINJA_TIMEOUT stop ninja after this many seconds and exit 0
#   NINJA_DEADLINE the same as a Unix time
#   NINJA_DRY_RUN  run ninja -n only (every input there?) and stop
#
# The Debian packages it needs are in the recipe's sudo: section (the scripts
# it calls are run with NO_APT=1 and never use apt themselves).
set -euo pipefail

cmd=${1:?prebuild or build} version=${2:?chromium version} cpu=${3:?arm, arm64 or x64}
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "bad version: $version"; exit 1; }
case "$cpu" in arm|arm64|x64) ;; *) echo "bad cpu: $cpu"; exit 1 ;; esac

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
export NO_APT=1 VERSION=$version DEPOT_TOOLS_UPDATE=0
PACKAGE_NAME=${PACKAGE_NAME:-org.chromium.chrome.fdroid}
JOBS=${JOBS:-$(nproc)}
# The toolchain and tools scripts expect this repository at ci/.
[ -e ci ] || ln -s . ci

# The F-Droid variant (fdroiddata#3911): androidx releases from Google Maven,
# microG instead of Play services, stubs for the rest, Play Core / ML Kit /
# Impress out, the small patches, the prebuilt Java build tools from Maven
# Central and Google Maven, and no Google sysroot.
VARIANT="androidx=release stubs genstubs gms=microg drop=playcore,mlkit,impress gnargs
  patch=cast,shape,castoff,status,fido,nogms tools=r8,turbine,aapt2,protoc,kotlinc nosysroot"
TOOLS_FROM_SOURCE="gperf esbuild tsc rollup-wasm golang"

depot_tools() {
  if [ -z "${DEPOT_TOOLS:-}" ]; then
    DEPOT_TOOLS=$root/depot_tools
    [ -d "$DEPOT_TOOLS" ] || git clone -q --depth 1 \
      https://chromium.googlesource.com/chromium/tools/depot_tools.git "$DEPOT_TOOLS"
  fi
  export PATH=$DEPOT_TOOLS:$PATH
}

prebuild() {
  depot_tools

  echo "== chromium/src $version"
  rm -rf src && git init -q src
  for i in 1 2 3 4; do
    git -C src fetch -q --depth 1 https://chromium.googlesource.com/chromium/src.git \
      "refs/tags/$version" && break
    sleep $((i * 60))
  done
  git -C src checkout -q FETCH_HEAD

  echo "== DEPS without the ones chrome_public_apk does not need (fdroid/skip-deps.txt)"
  echo "   and the ones build provides itself (fdroid/replaced-deps.txt)"
  # Deleted from src/DEPS: custom_deps = None would skip only the git ones.
  python3 -I fdroid/skip_deps.py src/DEPS fdroid/skip-deps.txt fdroid/replaced-deps.txt
  cat > .gclient <<GCLIENT
solutions = [{
  "name": "src",
  "url": "https://chromium.googlesource.com/chromium/src.git",
  "managed": False,
  "custom_deps": {},
  "custom_vars": {"checkout_pgo_profiles": False},
}]
target_os = ["android"]
GCLIENT
  # TODO: the hooks download Google's prebuilt clang, Rust, Node, GN and
  # Ninja, which build replaces; --nohooks plus the few hooks the build needs
  # would keep them out of the scanned tree.
  gclient sync --no-history -j 8

  echo "== delete the flagged files chrome_public_apk never reads"
  python3 -I fdroid/prune_binaries.py src "reports/$version/prune-list.txt.gz"
  # The androidx and android_deps libraries: build fetches them from Maven.
  python3 -I fdroid/maven_libs.py --delete src "reports/$version/cipd-pins.json"

  # GN and the build scripts run third_party/cpython3/host/bin/python3, which
  # the prune list removes: use Debian's Python.
  rm -rf src/third_party/cpython3/host
  mkdir -p src/third_party/cpython3/host/bin
  ln -s "$(command -v python3)" src/third_party/cpython3/host/bin/python3

  # TODO (not tried yet): Debian's JDK in place of the CIPD one. Chromium's
  # build reads third_party/jdk/current; the version must match DEPS.
  if [ -n "${JAVA_HOME:-}" ]; then
    echo "== JDK from the build server: $JAVA_HOME"
    rm -rf src/third_party/jdk/current
    ln -s "$JAVA_HOME" src/third_party/jdk/current
  fi

  echo "== NDK from the build server: ${ANDROID_NDK:?set ANDROID_NDK}"
  rm -rf src/third_party/android_toolchain/ndk
  mkdir -p src/third_party/android_toolchain
  ln -s "$ANDROID_NDK" src/third_party/android_toolchain/ndk
}

build() {
  depot_tools
  : "${ANDROID_NDK:?set ANDROID_NDK}"
  # A second run after an interrupted ninja (relay jobs on GitHub Actions)
  # skips straight to ninja: the toolchain, tools and variant are in place.
  if [ -f src/out/Default/.fdroid-configured ]; then
    echo "== configured already, continuing ninja"
  else
    configure
  fi
  run_ninja
}

configure() {

  echo "== toolchain from source (Debian's compilers): clang, Rust, GN, Ninja, Node"
  rm -rf pkg
  mkdir -p pkg
  [ -n "${TOOLCHAIN_PKG:-}" ] && cp -a "$TOOLCHAIN_PKG"/. pkg/
  # Build every part that TOOLCHAIN_PKG does not already provide.
  for part in clang-hostsys:clang rust-rustup:rust tools:tools; do
    [ -f "pkg/${part#*:}.tar.zst" ] || bash .github/scripts/toolchain_debian.sh "${part%%:*}"
  done
  python3 .github/scripts/swap_toolchain.py src pkg
  # V8's metagen loads libclang through its Python bindings (Google's
  # llvm-libclang package is in fdroid/replaced-deps.txt).
  python3 -I fdroid/llvm_libclang.py src
  # Crubit's generated headers go through clang-format (Google's package is
  # in fdroid/replaced-deps.txt): ours if the clang build has it, else Debian's.
  cf=src/third_party/llvm-build/Release+Asserts/bin/clang-format
  [ -x "$cf" ] || cf=$(command -v clang-format) || { echo "no clang-format (Debian package clang-format)"; exit 1; }
  mkdir -p src/buildtools/linux64-format
  ln -sfn "$(readlink -f "$cf")" src/buildtools/linux64-format/clang-format
  echo "clang-format: $(src/buildtools/linux64-format/clang-format --version)"

  echo "== prebuilt tools the build reads, from source: $TOOLS_FROM_SOURCE"
  rm -rf tools-build && mkdir tools-build
  if [ -n "${TOOLS_PKG:-}" ]; then
    cp -a "$TOOLS_PKG" tools-build/pkg
  else
    for tool in $TOOLS_FROM_SOURCE; do
      (cd tools-build && bash "$root/.github/scripts/tools_from_source.sh" "$tool")
    done
  fi
  python3 -I .github/scripts/swap_tools.py src tools-build/pkg
  rm -rf tools-build

  echo "== androidx and android_deps from Google Maven / Maven Central"
  pins=$root/reports/$version/cipd-pins.json
  [ -f "$pins" ] || { echo "no $pins: run sync-trim.yml for $version first"; exit 1; }
  # build_tools_maven.py (tools= below) reads the r8 and kotlinc versions there.
  export FDROID_CIPD_PINS=$pins
  python3 -I fdroid/maven_libs.py src "$pins"
  # Never released to Google Maven: build it from AOSP's source.
  python3 -I fdroid/sidecar_aar.py src

  echo "== F-Droid variant"
  # shellcheck disable=SC2086
  python3 .github/scripts/gms_variant.py src "$(echo $VARIANT)" > variant.gn

  echo "== gn gen ($cpu, $PACKAGE_NAME)"
  mkdir -p src/out/Default
  cat > src/out/Default/args.gn <<ARGS
target_os = "android"
target_cpu = "$cpu"
is_debug = false
is_component_build = false
symbol_level = 0
blink_symbol_level = 0
v8_symbol_level = 0
treat_warnings_as_errors = false
android_static_analysis = "off"
use_siso = false
use_mold = false
dcheck_always_on = false
chrome_public_manifest_package = "$PACKAGE_NAME"
ARGS
  cat variant.gn >> src/out/Default/args.gn
  (cd src && buildtools/linux64/gn gen out/Default)
  touch src/out/Default/.fdroid-configured
}

run_ninja() {
  echo "== ninja"
  if [ -n "${NINJA_DEADLINE:-}" ]; then
    left=$((NINJA_DEADLINE - $(date +%s)))
    # Both set: whichever comes first.
    [ -n "${NINJA_TIMEOUT:-}" ] && [ "$NINJA_TIMEOUT" -lt "$left" ] || NINJA_TIMEOUT=$left
  fi
  if [ -n "${NINJA_DRY_RUN:-}" ]; then
    # Test mode: check that every input of chrome_public_apk is there
    # (validations included) without compiling anything. ninja stops at the
    # first missing file, so first list every source path the .ninja files
    # name that does not exist.
    (cd src/out/Default && find . -name '*.ninja' -print0 | xargs -0 grep -oh '\.\./\.\./[^ :|$]*' \
      | sort -u | while read -r f; do [ -e "$f" ] || echo "${f#../../}"; done) > ninja-missing.txt
    if [ -s ninja-missing.txt ]; then
      echo "== $(wc -l < ninja-missing.txt) files the build graph names are missing (not all of them"
      echo "   need be chrome_public_apk inputs):"
      sed 's|/[^/]*$||' ninja-missing.txt | sort | uniq -c | sort -rn | head -40
      head -60 ninja-missing.txt
    fi
    src/third_party/ninja/ninja -C src/out/Default -n chrome_public_apk > ninja-dry-run.log
    echo "ninja -n chrome_public_apk: ok ($(wc -l < ninja-dry-run.log) lines)"
    return 0
  fi
  if [ -n "${NINJA_TIMEOUT:-}" ]; then
    [ "$NINJA_TIMEOUT" -gt 60 ] || { echo "no time left for ninja"; return 0; }
    rc=0
    timeout -s INT "$NINJA_TIMEOUT" src/third_party/ninja/ninja -C src/out/Default -j "$JOBS" \
      chrome_public_apk || rc=$?
    if [ "$rc" = 124 ]; then echo "ninja stopped after ${NINJA_TIMEOUT}s (NINJA_TIMEOUT)"; return 0; fi
    [ "$rc" = 0 ] || exit "$rc"
  else
    src/third_party/ninja/ninja -C src/out/Default -j "$JOBS" chrome_public_apk
  fi

  mkdir -p fdroid-out
  python3 -I fdroid/unsign_apk.py src/out/Default/apks/ChromePublic.apk \
    fdroid-out/ChromePublic-unsigned.apk
}

"$cmd"
