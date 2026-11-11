#!/usr/bin/env python3
"""Replace the prebuilt toolchain that gclient synced into a Chromium checkout
with the one built by chromium-toolchain.yml, and write a report comparing
the two to <src>/toolchain-report.md.

Usage: swap_toolchain.py <chromium src dir> <dir with *.tar.zst artifacts>
"""

import hashlib
import os
import shutil
import subprocess
import sys

CLANG = 'third_party/llvm-build/Release+Asserts'
RUST = 'third_party/rust-toolchain'
NODE = 'third_party/node/linux/node-linux-x64'
GN = 'buildtools/linux64/gn'
NINJA = 'third_party/ninja/ninja'

# (name, binary to fingerprint, version command)
CHECKS = [
    ('clang', f'{CLANG}/bin/clang', ['--version']),
    ('lld', f'{CLANG}/bin/lld', None),
    ('rustc', f'{RUST}/bin/rustc', ['-V']),
    ('bindgen', f'{RUST}/bin/bindgen', ['--version']),
    ('gn', GN, ['--version']),
    ('ninja', NINJA, ['--version']),
    ('node', f'{NODE}/bin/node', ['--version']),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def fingerprint(src):
    out = {}
    for name, rel, cmd in CHECKS:
        path = os.path.join(src, rel)
        if not os.path.exists(path):
            out[name] = ('missing', '')
            continue
        ver = ''
        if cmd:
            r = subprocess.run([path] + cmd, capture_output=True, text=True)
            ver = (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else f'exit {r.returncode}'
        out[name] = (sha256(path), ver)
    return out


def listing(root):
    files = set()
    for d, dirs, names in os.walk(root):
        for n in names + [x for x in dirs if os.path.islink(os.path.join(d, x))]:
            files.add(os.path.relpath(os.path.join(d, n), root))
    return files


def replace_dir(src, staged, rel):
    dst = os.path.join(src, rel)
    if os.path.lexists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(os.path.join(staged, rel), dst)


def replace_file(src, staged, rel):
    dst = os.path.join(src, rel)
    os.remove(dst)
    shutil.move(os.path.join(staged, rel), dst)
    os.chmod(dst, 0o755)


def main():
    src, tc = sys.argv[1], sys.argv[2]
    staged = os.path.join(tc, 'staged')
    os.makedirs(staged, exist_ok=True)
    for name in sorted(os.listdir(tc)):
        if name.endswith('.tar.zst'):
            print(f'extracting {name}')
            subprocess.run(
                f'zstd -d -T0 -c "{os.path.join(tc, name)}" | tar -xf - -C "{staged}"',
                shell=True,
                check=True,
            )

    before = fingerprint(src)
    google_clang = listing(os.path.join(src, CLANG))
    google_rust = listing(os.path.join(src, RUST))

    replace_dir(src, staged, CLANG)
    # Our clang build keeps every LLVM tool; keep only the ones Google ships.
    bin_dir = os.path.join(src, CLANG, 'bin')
    for n in os.listdir(bin_dir):
        if f'bin/{n}' not in google_clang:
            os.remove(os.path.join(bin_dir, n))
    replace_dir(src, staged, RUST)
    replace_dir(src, staged, NODE)
    replace_file(src, staged, GN)
    replace_file(src, staged, NINJA)

    after = fingerprint(src)
    missing_clang = sorted(google_clang - listing(os.path.join(src, CLANG)))
    missing_rust = sorted(google_rust - listing(os.path.join(src, RUST)))

    lines = [
        '## Toolchain: Google prebuilt vs built from source',
        '',
        '| | Google sha256 | ours sha256 | Google version | ours version |',
        '|---|---|---|---|---|',
    ]
    for name, _, _ in CHECKS:
        b, a = before[name], after[name]
        lines.append(f'| {name} | `{b[0]}` | `{a[0]}` | {b[1]} | {a[1]} |')
    for title, missing in (('clang', missing_clang), ('rust', missing_rust)):
        lines += ['', f'{title}: {len(missing)} files in Google package not in ours']
        lines += [f'- `{m}`' for m in missing[:60]]
    report = '\n'.join(lines) + '\n'
    print(report)
    with open(os.path.join(src, 'toolchain-report.md'), 'w') as f:
        f.write(report)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write(report)

    for name, rel, _ in CHECKS:
        if before[name][0] != 'missing' and after[name][0] == before[name][0]:
            sys.exit(f'{name} still is the Google binary')
        if after[name][0] == 'missing' and before[name][0] != 'missing':
            sys.exit(f'{name} missing after swap')
    shutil.rmtree(tc)


if __name__ == '__main__':
    main()
