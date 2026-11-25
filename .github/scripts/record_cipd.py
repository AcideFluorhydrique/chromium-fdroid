#!/usr/bin/env python3
"""Record what the CIPD packages that fdroid/build.sh rebuilds from Maven hold.

Usage: record_cipd.py <chromium src dir> <out.json>

The packages are pinned in DEPS by CIPD instance id only, with no version:
r8 and turbine are built from their main branches, androidx partly from
snapshots. sync-trim.yml (a full gclient sync on GitHub Actions) writes this
file per Chromium version to reports/<version>/cipd-pins.json; build.sh then
knows which files to fetch from Google Maven / Maven Central, which versions
to ask for, and can tell whether what Maven has is byte-identical.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

DIRS = [
    'third_party/androidx/cipd',
    'third_party/android_deps/cipd',
    'third_party/kotlinc/current',
    'third_party/r8/cipd',
    'third_party/turbine/cipd',
    'third_party/android_build_tools/aapt2/cipd',
    'third_party/android_build_tools/protoc/cipd',
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    src, out = sys.argv[1:3]
    files = {}
    for d in DIRS:
        root = os.path.join(src, d)
        for dirpath, dirnames, names in os.walk(root):
            dirnames[:] = [n for n in dirnames if n != '.cipd']
            for n in names:
                p = os.path.join(dirpath, n)
                if os.path.isfile(p) and not os.path.islink(p):
                    files[os.path.relpath(p, src)] = sha256(p)
    java = os.path.join(src, 'third_party/jdk/current/bin/java')
    r8 = os.path.join(src, 'third_party/r8/cipd/lib/r8.jar')
    r8_out = subprocess.run([java, '-cp', r8, 'com.android.tools.r8.R8', '--version'],
                            capture_output=True, text=True).stdout
    bt = os.path.join(src, 'third_party/kotlinc/current/build.txt')
    pins = {
        'r8_version': (re.search(r'R8 (\S+)', r8_out) or [None, None])[1],
        'kotlinc_build': open(bt).read().strip() if os.path.exists(bt) else None,
        'files': dict(sorted(files.items())),
    }
    with open(out, 'w') as f:
        json.dump(pins, f, indent=1)
        f.write('\n')
    print(f"{out}: r8 {pins['r8_version']}, kotlinc {pins['kotlinc_build']}, {len(files)} files")


if __name__ == '__main__':
    main()
