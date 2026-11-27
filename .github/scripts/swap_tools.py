#!/usr/bin/env python3
"""Put the prebuilt tools built from source by tools-from-source.yml into a
Chromium checkout, in place of the copies gclient sync downloaded.

Usage: swap_tools.py <chromium src dir> <dir with the tool files>

Every tool must be in the tool directory; each replaced file is printed with the sha256 of
both versions.
"""

import hashlib
import os
import shutil
import subprocess
import sys

# file from tools-from-source.yml -> (path in src, executable)
TOOLS = {
    'gperf': ('third_party/gperf/cipd/bin/gperf', True),
    'esbuild': ('third_party/devtools-frontend/src/third_party/esbuild/esbuild', True),
    'tsc': ('third_party/typescript/linux-amd64/src/lib/tsc', True),
    'rollup-wasm': ('third_party/node/node_modules/@rollup/wasm-node/dist/wasm-node/bindings_wasm_bg.wasm', False),
    'rollup-wasm.js': ('third_party/node/node_modules/@rollup/wasm-node/dist/wasm-node/bindings_wasm.js', False),
}


# GOROOT tarball -> directory it replaces (Dawn's code generator runs this Go).
DIRS = {
    'golang': 'third_party/dawn/tools/golang/linux-amd64',
}


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main():
    src, tools = sys.argv[1:3]
    missing = [n for n in list(TOOLS) + list(DIRS) if not os.path.isfile(os.path.join(tools, n))]
    if missing:
        sys.exit(f'missing from {tools}: {" ".join(missing)}')
    lines = ['## Prebuilt tools built from source', '', '| tool | path | before | after |', '|---|---|---|---|']
    for name, (rel, exe) in TOOLS.items():
        dst = os.path.join(src, rel)
        if os.path.exists(dst):
            before = sha(dst)
            os.chmod(os.path.dirname(dst), 0o755)
            os.chmod(dst, 0o644)
            os.remove(dst)
        else:
            # Not synced (fdroid/replaced-deps.txt).
            before = 'not synced'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(tools, name), dst)
        os.chmod(dst, 0o755 if exe else 0o644)
        lines.append(f'| {name} | `{rel}` | `{before}` | `{sha(dst)}` |')
    for name, rel in DIRS.items():
        dst = os.path.join(src, rel)
        if os.path.isdir(dst):
            subprocess.run(['chmod', '-R', 'u+w', dst], check=True)
            shutil.rmtree(dst)
        os.makedirs(dst)
        subprocess.run(['tar', '-C', dst, '-xzf', os.path.join(tools, name)], check=True)
        ver = subprocess.run([os.path.join(dst, 'bin', 'go'), 'version'], capture_output=True, text=True).stdout.strip()
        lines.append(f'| {name} | `{rel}` | (directory) | {ver} |')
    text = '\n'.join(lines) + '\n'
    print(text)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write(text)


if __name__ == '__main__':
    main()
