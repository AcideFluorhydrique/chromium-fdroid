#!/bin/bash
# Build one of the prebuilt tools chrome_public_apk reads (#7, #8) from source
# inside a Debian container, at the version Chromium pins.
#
# Usage: VERSION=<chromium tag> tools_from_source.sh gperf|esbuild|tsc
# Writes pkg/<tool> and appends a line to pkg/<tool>.md.
set -euo pipefail

tool=$1
export DEBIAN_FRONTEND=noninteractive
for i in 1 2 3 4 5; do
  apt-get update -q -o Acquire::Retries=5 && apt-get install -y -q -o Acquire::Retries=5 \
    ca-certificates curl git build-essential golang-go && break
  sleep 60
done
git config --global --add safe.directory '*'

# Build Go $1 (e.g. 1.26 or 1.26.2) from source, bootstrapped from Debian's
# golang-go, through the newest 1.24.x if Debian's Go is too old. Prints GOROOT.
build_go() {
  local want=$1 boot=/usr/lib/go tag
  tag=$(git ls-remote --tags https://github.com/golang/go | grep -oP "refs/tags/\Kgo${want//./\\.}(\.[0-9]+)?$" | sort -V | tail -1)
  [ -n "$tag" ] || { echo "no Go tag for $want" >&2; return 1; }
  build_one() {  # tag bootstrap-root
    rm -rf "go-$1" && git clone -q --depth 1 -b "$1" https://github.com/golang/go.git "go-$1" >&2
    (cd "go-$1/src" && GOROOT_BOOTSTRAP=$2 GOTOOLCHAIN=local ./make.bash >&2)
  }
  if ! build_one "$tag" "$boot"; then
    local mid
    mid=$(git ls-remote --tags https://github.com/golang/go | grep -oP 'refs/tags/\Kgo1\.24\.[0-9]+$' | sort -V | tail -1)
    echo "Debian's Go cannot bootstrap $tag; building $mid first" >&2
    build_one "$mid" "$boot"
    build_one "$tag" "$PWD/go-$mid"
  fi
  echo "$PWD/go-$tag"
}

gitiles() { curl -fsSL "https://chromium.googlesource.com/$1?format=TEXT" | base64 -d; }
deps=$(gitiles "chromium/src/+/refs/tags/$VERSION/DEPS")
mkdir -p pkg

case "$tool" in
gperf)
  v=$(grep -A12 "'src/third_party/gperf'" <<<"$deps" | grep -oP "version:\d+@\K[0-9.]+(?=\.chromium)" | head -1)
  echo "gperf $v"
  curl -fsSL "https://ftp.gnu.org/gnu/gperf/gperf-$v.tar.gz" | tar -xz
  (cd "gperf-$v" && ./configure -q && make -s -j"$(nproc)")
  cp "gperf-$v/src/gperf" pkg/gperf
  ver=$(pkg/gperf --version | head -1)
  ;;
esbuild)
  rev=$(grep -oP "'devtools_frontend_revision': '\K[0-9a-f]+" <<<"$deps")
  ddeps=$(gitiles "devtools/devtools-frontend/+/$rev/DEPS")
  v=$(grep -B2 -A12 "esbuild" <<<"$ddeps" | grep -oP "version:\d+@\K[0-9]+\.[0-9]+\.[0-9]+" | head -1)
  echo "devtools-frontend $rev, esbuild $v"
  git clone -q --depth 1 -b "v$v" https://github.com/evanw/esbuild.git esbuild-src
  (cd esbuild-src && go version && GOTOOLCHAIN=local CGO_ENABLED=0 go build -trimpath -o ../pkg/esbuild ./cmd/esbuild)
  ver="esbuild $(pkg/esbuild --version)"
  ;;
tsc)
  v=$(grep -A10 "'src/third_party/typescript/linux-amd64/src'" <<<"$deps" | grep -oP "version:\d+@\K[0-9.]+" | head -1)
  echo "typescript $v"
  tag=$(git ls-remote --tags https://github.com/microsoft/typescript-go | grep -oP "refs/tags/\K(typescript/)?v?${v//./\\.}$" | head -1 || true)
  [ -n "$tag" ] || { echo "no typescript-go tag for $v; tags:"; git ls-remote --tags https://github.com/microsoft/typescript-go | tail -20; exit 1; }
  git clone -q --depth 1 -b "$tag" https://github.com/microsoft/typescript-go.git tsgo-src
  gover=$(grep -oP '^toolchain go\K[0-9.]+' tsgo-src/go.mod || grep -oP '^go \K[0-9.]+' tsgo-src/go.mod)
  echo "typescript-go needs Go $gover; Debian has $(go version)"
  goroot=$(build_go "$gover")
  export PATH="$goroot/bin:$PATH"
  (cd tsgo-src && go version && GOTOOLCHAIN=local CGO_ENABLED=0 go build -trimpath -o ../pkg/tsc ./cmd/tsgo)
  ver="tsc $(pkg/tsc --version 2>&1 | head -1)"
  ;;
rollup-wasm)
  # third_party/node/node_modules ships @rollup/wasm-node's prebuilt
  # bindings_wasm_bg.wasm; build it from rollup's Rust source with Debian's
  # rustc and its wasm32 std, then run rollup with it.
  v=$(gitiles "chromium/src/+/refs/tags/$VERSION/third_party/node/package.json" | grep -oP '"@rollup/wasm-node": "\K[0-9.]+')
  echo "@rollup/wasm-node $v"
  for i in 1 2 3; do apt-get install -y -q rustc cargo libstd-rust-dev-wasm32 lld binaryen nodejs npm && break; sleep 60; done
  rustc --version
  git clone -q --depth 1 -b "v$v" https://github.com/rollup/rollup.git rollup-src
  bg=$(grep -A2 'name = "wasm-bindgen"' rollup-src/rust/Cargo.lock | grep -oP 'version = "\K[^"]+')
  echo "wasm-bindgen $bg"
  cargo install -q --locked wasm-bindgen-cli --version "$bg" --root "$PWD/wb"
  (cd rollup-src/rust && RUSTFLAGS="-C opt-level=z" cargo build -q --locked --release \
    --target wasm32-unknown-unknown -p bindings_wasm)
  wb/bin/wasm-bindgen --target nodejs --out-dir wasm-node \
    rollup-src/rust/target/wasm32-unknown-unknown/release/bindings_wasm.wasm
  wasm-opt -Oz wasm-node/bindings_wasm_bg.wasm -o wasm-node/bindings_wasm_bg.wasm || true
  # Compare with the npm package and use ours in it for a real bundle.
  mkdir npm-test && (cd npm-test && npm pack -s "@rollup/wasm-node@$v" && tar -xzf rollup-wasm-node-$v.tgz)
  theirs=npm-test/package/dist/wasm-node/bindings_wasm_bg.wasm
  echo "npm:  $(stat -c %s $theirs) bytes $(sha256sum $theirs | cut -c1-16)"
  echo "ours: $(stat -c %s wasm-node/bindings_wasm_bg.wasm) bytes $(sha256sum wasm-node/bindings_wasm_bg.wasm | cut -c1-16)"
  cp wasm-node/bindings_wasm_bg.wasm wasm-node/bindings_wasm.js npm-test/package/dist/wasm-node/
  printf 'import {b} from "./b.js";\nconsole.log(b + 1);\n' > a.js
  printf 'export const b = 41;\nexport const unused = 0;\n' > b.js
  (cd npm-test/package && npm install -s --omit=dev --ignore-scripts >/dev/null 2>&1 || true)
  node npm-test/package/dist/bin/rollup a.js --format es | tee bundle.txt
  grep -q "41" bundle.txt && ! grep -q unused bundle.txt
  cp wasm-node/bindings_wasm_bg.wasm pkg/rollup-wasm
  ver="rollup $v wasm (wasm-bindgen $bg, $(rustc --version | cut -d' ' -f2)); bundles with it"
  ;;
esac
file "pkg/$tool" 2>/dev/null || true
echo "| $tool | $ver | $(sha256sum "pkg/$tool" | cut -c1-16) |" | tee "pkg/$tool.md"
