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
esac
file "pkg/$tool" 2>/dev/null || true
echo "| $tool | $ver | $(sha256sum "pkg/$tool" | cut -c1-16) |" | tee "pkg/$tool.md"
