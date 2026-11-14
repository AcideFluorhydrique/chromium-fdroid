#!/usr/bin/env python3
"""Make Chromium's toolchain build scripts fail instead of downloading
prebuilt compilers or CMake, so a run that succeeds really used the host
toolchain.

Usage: patch_toolchain_scripts.py <chromium src dir> [--rust]
"""

import os
import sys


def patch(path, old, new):
    with open(path) as f:
        s = f.read()
    if s.count(old) != 1:
        sys.exit(f'{path}: expected exactly one occurrence of {old!r}')
    with open(path, 'w') as f:
        f.write(s.replace(old, new))
    print(f'patched {path}: {old.splitlines()[0]!r}')


def main():
    src = sys.argv[1]
    build_py = os.path.join(src, 'tools/clang/scripts/build.py')

    patch(
        build_py,
        'def DownloadPinnedClang():\n',
        'def DownloadPinnedClang():\n'
        "  raise RuntimeError('prebuilt pinned clang is disabled')\n\n\n"
        'def _UnusedDownloadPinnedClang():\n',
    )
    patch(
        build_py,
        'def AddCMakeToPath():\n',
        'def AddCMakeToPath():\n'
        '  return\n\n\n'
        'def _UnusedAddCMakeToPath():\n',
    )
    # riscv64 runtimes target Android API 37, which the stable NDK on the
    # runner does not have yet. Chromium for arm64 phones does not need them.
    patch(
        build_py,
        "['aarch64', 'arm', 'i686', 'riscv64', 'x86_64']",
        "['aarch64', 'arm', 'i686', 'x86_64']",
    )

    # With OWN_HOST_SYSROOT set (toolchain_debian.sh sets it to / for the
    # Rust build), host tools are built against that system instead of
    # Chromium's prebuilt Debian sysroot, so Debian's own static libraries
    # (OpenSSL, ncursesw) link.
    patch(
        build_py,
        'def DownloadDebianSysroot(platform_name, skip_download=False):\n',
        'def DownloadDebianSysroot(platform_name, skip_download=False):\n'
        "  if platform_name == 'amd64' and os.environ.get('OWN_HOST_SYSROOT'):\n"
        "    return os.environ['OWN_HOST_SYSROOT']\n",
    )

    if '--rust' in sys.argv[2:]:
        patch(
            os.path.join(src, 'tools/rust/build_rust.py'),
            "        '--without-zstd',\n",
            "        '--without-zstd',\n"
            "        '--host-cc=' + os.environ['HOST_CC'],\n"
            "        '--host-cxx=' + os.environ['HOST_CXX'],\n",
        )
        # Chromium only needs cc_bindings_from_rs; rs_bindings_from_cc also
        # needs Abseil and nothing in Chromium uses it yet.
        patch(
            os.path.join(src, 'tools/rust/build_crubit.py'),
            'ENABLE_BUILDING_RS_BINDINGS_FROM_CC = True\n',
            'ENABLE_BUILDING_RS_BINDINGS_FROM_CC = False\n',
        )
        # With OWN_NCURSESW_DIR set (e.g. to Debian's libncurses-dev, see
        # toolchain_debian.sh), use it instead of the CIPD static build.
        patch(
            os.path.join(src, 'tools/rust/build_bindgen.py'),
            'def FetchNcurseswLibrary():\n',
            'def FetchNcurseswLibrary():\n'
            "    if os.environ.get('OWN_NCURSESW_DIR'):\n"
            "        return os.environ['OWN_NCURSESW_DIR']\n",
        )
        # The prebuilt OpenSSL 1.1.1 from CIPD is older than what curl-sys
        # in cargo needs; use the OpenSSL 3 that chromium-toolchain.yml
        # builds from source against the same Debian sysroot.
        patch(
            os.path.join(src, 'tools/rust/build_rust.py'),
            'def AddOpenSSLToEnv():\n',
            'def AddOpenSSLToEnv():\n'
            "    os.environ['OPENSSL_DIR'] = os.environ['OWN_OPENSSL_DIR']\n\n\n"
            'def _UnusedAddOpenSSLToEnv():\n',
        )
        # With OWN_STAGE0_DIR set (a rustup toolchain, e.g. from Debian's
        # rustup, at the version in src/stage0), use it as the stage0 compiler
        # and the beta sysroot instead of downloading Rust's tarballs.
        if os.environ.get('OWN_STAGE0_DIR'):
            br = os.path.join(src, 'tools/rust/build_rust.py')
            patch(br, "def FetchBetaPackage(name, triple=None):\n",
                  "def FetchBetaPackage(name, triple=None):\n"
                  "    if os.environ.get('OWN_STAGE0_DIR'):\n"
                  "        return None\n"
                  "    return _UnusedFetchBetaPackage(name, triple)\n\n\n"
                  "def _UnusedFetchBetaPackage(name, triple=None):\n")
            patch(br, "def InstallRustBetaSysroot(target_triples):\n",
                  "def InstallRustBetaSysroot(target_triples):\n"
                  "    if os.environ.get('OWN_STAGE0_DIR'):\n"
                  "        if os.path.exists(RUST_BETA_SYSROOT_DIR):\n"
                  "            RmTree(RUST_BETA_SYSROOT_DIR)\n"
                  "        shutil.copytree(os.environ['OWN_STAGE0_DIR'], RUST_BETA_SYSROOT_DIR, symlinks=True)\n"
                  "        return\n")
            patch(br, "            cargo_bin = os.path.join(path, 'cargo', 'bin', 'cargo')\n",
                  "            cargo_bin = os.path.join(os.environ['OWN_STAGE0_DIR'], 'bin', 'cargo')\n")
            d = os.environ['OWN_STAGE0_DIR']
            patch(os.path.join(src, 'tools/rust/config.toml.template'), '[build]\n',
                  f'[build]\nrustc = "{d}/bin/rustc"\ncargo = "{d}/bin/cargo"\n')


if __name__ == '__main__':
    main()
