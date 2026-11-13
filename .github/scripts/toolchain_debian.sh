#!/bin/bash
# Build one part of Chromium's toolchain inside a Debian container, using
# Debian's packages as the starting point (F-Droid's build server runs Debian).
#
# Usage (from the workspace that holds src/ and ci/):
#   toolchain_debian.sh clang|rust|tools
#
# Writes pkg/<part>.tar.zst, the same artifact layout as toolchain.yml.
set -euo pipefail

part=$1
ws=$(pwd)
export DEBIAN_FRONTEND=noninteractive

apt_install() {
  for i in 1 2 3 4 5; do
    apt-get update -q -o Acquire::Retries=5 && apt-get install -y -q -o Acquire::Retries=5 "$@" && return
    echo "apt failed, retrying in 60s ($i/5)"; sleep 60
  done
  return 1
}

apt_install ca-certificates curl git python3 python3-setuptools xz-utils zstd file \
  build-essential clang lld llvm cmake ninja-build pkg-config zlib1g-dev
export HOST_CC=/usr/bin/clang HOST_CXX=/usr/bin/clang++
# The checkout belongs to the runner user; git runs as root in the container.
git config --global --add safe.directory '*'
clang --version | head -1
gcc --version | head -1

case "$part" in
clang)
  # The Android NDK from F-Droid's sdkmanager, at the version Chromium pins.
  apt_install sdkmanager
  ndk=$(grep -oP "'android_ndk_version': Str\('\d+@\K[0-9.]+" src/DEPS)
  echo "NDK $ndk"
  export ANDROID_HOME=$ws/android-sdk
  mkdir -p "$ANDROID_HOME"
  yes | sdkmanager --sdk_root="$ANDROID_HOME" "ndk;$ndk"
  mkdir -p src/third_party/android_toolchain
  rm -rf src/third_party/android_toolchain/ndk
  ln -s "$ANDROID_HOME/ndk/$ndk" src/third_party/android_toolchain/ndk

  python3 ci/.github/scripts/patch_toolchain_scripts.py src
  python3 src/tools/clang/scripts/build.py \
    --disable-asserts \
    --host-cc="$HOST_CC" --host-cxx="$HOST_CXX" \
    --use-system-cmake \
    --without-fuchsia \
    --with-android \
    --with-ml-inliner-model=

  d=src/third_party/llvm-build/Release+Asserts
  "$d/bin/clang" --version | head -1
  mkdir -p pkg
  tar -C src -cf - "third_party/llvm-build/Release+Asserts/bin" \
    "third_party/llvm-build/Release+Asserts/lib/clang" \
    "third_party/llvm-build/Release+Asserts/cr_build_revision" | zstd -T0 -6 > pkg/clang.tar.zst
  ;;

rust)
  apt_install libssl-dev libncurses-dev
  # Debian's OpenSSL 3 and ncursesw instead of the CIPD prebuilts. Only the
  # static libraries and their headers are exposed, so nothing else from the
  # host leaks into the build, which links against Chromium's Debian sysroot.
  multiarch=$(gcc -print-multiarch)
  ssl=$ws/debian-openssl
  rm -rf "$ssl" && mkdir -p "$ssl/lib" "$ssl/include"
  cp /usr/lib/$multiarch/libssl.a /usr/lib/$multiarch/libcrypto.a "$ssl/lib/"
  cp -r /usr/include/openssl "$ssl/include/"
  cp /usr/include/$multiarch/openssl/* "$ssl/include/openssl/"
  export OWN_OPENSSL_DIR=$ssl OPENSSL_STATIC=1
  nc=$ws/debian-ncursesw
  rm -rf "$nc" && mkdir -p "$nc/lib" "$nc/include"
  cp /usr/lib/$multiarch/libncursesw.a /usr/lib/$multiarch/libtinfo.a "$nc/lib/"
  cp /usr/include/{curses.h,ncurses.h,ncurses_dll.h,term.h,termcap.h,unctrl.h} "$nc/include/" 2>/dev/null || true
  [ -d /usr/include/ncursesw ] && cp -r /usr/include/ncursesw "$nc/include/"
  export OWN_NCURSESW_DIR=$nc
  ls "$ssl/lib" "$nc/lib"

  python3 ci/.github/scripts/patch_toolchain_scripts.py src --rust
  python3 src/tools/rust/build_rust.py --build-bindgen --build-crubit --skip-test

  d=src/third_party/rust-toolchain
  for f in "$d"/bin/*; do [ -L "$f" ] || strip "$f" || true; done
  "$d/bin/rustc" -vV
  mkdir -p pkg
  tar -C src -cf - third_party/rust-toolchain | zstd -T0 -6 > pkg/rust.tar.zst
  ;;

tools)
  gn_rev=$(grep -oP "'gn_version': 'git_revision:\K[0-9a-f]+" src/DEPS)
  ninja_ver=$(grep -oP "'ninja_version': 'version:[0-9]+@\K[0-9]+\.[0-9]+\.[0-9]+" src/DEPS)
  node_ver=$(grep -oP '^NODE_VERSION="\Kv[0-9.]+' src/third_party/node/update_node_binaries)
  echo "gn $gn_rev / ninja $ninja_ver / node $node_ver"
  out=$ws/out

  git clone -q --depth 1 -b "v$ninja_ver" https://github.com/ninja-build/ninja.git ninja-src
  (cd ninja-src && CXX="$HOST_CXX" python3 configure.py --bootstrap)
  install -D -m755 ninja-src/ninja "$out/third_party/ninja/ninja"

  git clone -q https://gn.googlesource.com/gn gn-src
  (cd gn-src && git checkout -q "$gn_rev" \
    && extra="" && { python3 build/gen.py --help | grep -q -- --allow-warnings && extra=--allow-warnings || true; } \
    && CC=gcc CXX=g++ AR=ar CXXFLAGS=-Wno-comment python3 build/gen.py $extra \
    && "$out/third_party/ninja/ninja" -C out gn)
  install -D -m755 gn-src/out/gn "$out/buildtools/linux64/gn"

  curl -fsSL "https://nodejs.org/dist/$node_ver/node-$node_ver.tar.gz" | tar -xz
  prefix="$out/third_party/node/linux/node-linux-x64"
  (cd "node-$node_ver" && ./configure --prefix="$prefix" && make -j"$(nproc)" install)
  rm -f "$prefix/bin/corepack"
  "$prefix/bin/node" --version

  mkdir -p pkg
  tar -C "$out" -cf - . | zstd -T0 -6 > pkg/tools.tar.zst
  ;;
esac
ls -lh pkg
