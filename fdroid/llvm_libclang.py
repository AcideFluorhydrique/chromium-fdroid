#!/usr/bin/env python3
"""Put together third_party/llvm-libclang from the toolchain built from source.

Usage: llvm_libclang.py <chromium src dir>

Google's llvm-libclang package (fdroid/replaced-deps.txt: not synced) holds
lib/libclang.so, clang's C API headers and the Python bindings; V8's metagen
loads the library through the bindings at build time. The library is the one
build_bindgen.py copied into our Rust toolchain (same LLVM revision as our
clang); the headers and bindings are source files from llvm-project at the
revision our clang reports.
"""

import base64
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

LLVM_GIT = 'https://chromium.googlesource.com/external/github.com/llvm/llvm-project'


def fetch(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except OSError as e:
            if i == 4:
                raise
            print(f'retry {url}: {e}')
            time.sleep(10 * (i + 1))


def gitiles_file(rev, path):
    return base64.b64decode(fetch(f'{LLVM_GIT}/+/{rev}/{path}?format=TEXT'))


def gitiles_dir(rev, path):
    text = fetch(f'{LLVM_GIT}/+/{rev}/{path}?format=JSON').decode()
    return [e['name'] for e in json.loads(text[text.index('{'):])['entries'] if e['type'] == 'blob']


def main():
    src = sys.argv[1]
    clang = os.path.join(src, 'third_party/llvm-build/Release+Asserts/bin/clang')
    version = subprocess.run([clang, '--version'], capture_output=True, text=True, check=True).stdout
    rev = re.search(r'llvm-project ([0-9a-f]{40})', version)[1]

    rust_lib = os.path.join(src, 'third_party/rust-toolchain/lib')
    libs = sorted(glob.glob(os.path.join(rust_lib, 'libclang.so*')), key=len)
    if not libs:
        sys.exit(f'no libclang.so in {rust_lib}')

    out = os.path.join(src, 'third_party/llvm-libclang')
    if os.path.lexists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'lib'))
    # Follow the symlinks: one real file named libclang.so, as in Google's package.
    shutil.copy2(os.path.realpath(libs[0]), os.path.join(out, 'lib', 'libclang.so'))

    files = ['bindings/python/clang/__init__.py', 'bindings/python/clang/cindex.py']
    files += [f'include/clang-c/{n}' for n in gitiles_dir(rev, 'clang/include/clang-c') if n.endswith('.h')]
    for rel in files:
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(gitiles_file(rev, f'clang/{rel}'))
    print(f'third_party/llvm-libclang: libclang.so from {os.path.basename(libs[0])}, '
          f'{len(files)} files from llvm-project {rev[:12]}')


if __name__ == '__main__':
    main()
