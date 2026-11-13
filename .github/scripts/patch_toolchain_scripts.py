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


if __name__ == '__main__':
    main()
