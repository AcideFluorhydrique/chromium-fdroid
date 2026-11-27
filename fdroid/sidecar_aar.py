#!/usr/bin/env python3
"""Build androidx.window.sidecar's sidecar.aar from its source.

Usage: sidecar_aar.py <chromium src dir>

Chromium takes androidx.window.sidecar:sidecar as a snapshot from androidx.dev;
it was never released to Google Maven (fdroid/maven_libs.py cannot fetch it).
It is a stub library of five Java interfaces and classes (the deprecated OEM
window extension API) in AOSP's androidx repository; gn gen reads every aar,
so build compiles it with javac and packs it the way an aar is laid out.
"""

import base64
import glob
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

AOSP = 'https://android.googlesource.com/platform/frameworks/support'
# androidx-main when this was written; the stubs rarely change.
REVISION = 'b8c1bf854add0e2abb7e2f37de9938ad1531f3f9'
DIR = 'window/sidecar/sidecar/src/main/java'
OUT = 'third_party/androidx/cipd/libs/androidx_window_sidecar_sidecar/sidecar.aar'
MANIFEST = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    package="androidx.window.sidecar" />\n')


def fetch(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except OSError:
            if i == 4:
                raise
            time.sleep(10 * (i + 1))


def walk(path):
    text = fetch(f'{AOSP}/+/{REVISION}/{path}?format=JSON').decode()
    for e in json.loads(text[text.index('{'):])['entries']:
        p = f"{path}/{e['name']}"
        if e['type'] == 'tree':
            yield from walk(p)
        elif p.endswith('.java'):
            yield p


def one(pattern):
    hits = sorted(glob.glob(pattern))
    if not hits:
        sys.exit(f'sidecar_aar: nothing matches {pattern}')
    return hits[-1]


def main():
    src = sys.argv[1]
    tmp = tempfile.mkdtemp()
    java_dir, classes = os.path.join(tmp, 'java'), os.path.join(tmp, 'classes')
    files = []
    for p in walk(DIR):
        dst = os.path.join(java_dir, os.path.relpath(p, DIR))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(base64.b64decode(fetch(f'{AOSP}/+/{REVISION}/{p}?format=TEXT')))
        files.append(dst)
    cp = [
        one(os.path.join(src, 'third_party/android_sdk/public/platforms/android-*/android.jar')),
        one(os.path.join(src, 'third_party/android*/cipd/libs/androidx_annotation_annotation_jvm/*.jar')),
        one(os.path.join(src, 'third_party/android_deps/cipd/libs/org_jspecify_jspecify/*.jar')),
    ]
    javac = os.path.join(src, 'third_party/jdk/current/bin/javac')
    subprocess.run([javac, '-nowarn', '--release', '11', '-cp', ':'.join(cp), '-d', classes] + files,
                   check=True)
    jar = os.path.join(tmp, 'classes.jar')
    with zipfile.ZipFile(jar, 'w', zipfile.ZIP_DEFLATED) as z:
        for d, _, names in sorted(os.walk(classes)):
            for n in sorted(names):
                z.write(os.path.join(d, n), os.path.relpath(os.path.join(d, n), classes))
    out = os.path.join(src, OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('AndroidManifest.xml', MANIFEST)
        z.write(jar, 'classes.jar')
        z.writestr('R.txt', '')
    print(f'sidecar_aar: built {OUT} from {len(files)} files of AOSP androidx {REVISION[:12]}')


if __name__ == '__main__':
    main()
