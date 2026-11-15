#!/usr/bin/env python3
"""Report the prebuilt Android build tools that chrome_public_apk uses.

Usage: android_tools.py <src dir> <build-inputs.txt> <output dir>

For every CIPD package in DEPS under third_party/ that looks like an Android
build tool (android_build_tools/*, kotlinc, jdk, android_sdk, r8, ...):
  - its CIPD package and version tags (from `cipd describe`),
  - how many of its files the build graph reads,
  - for the tools that Google publishes on Maven (aapt2, bundletool,
    manifest-merger, lint), whether that version is on Google Maven and
    whether the CIPD file is the Maven file.

Writes android-tools.md and android-tools.tsv.
"""

import collections
import hashlib
import io
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile

GOOGLE = 'https://dl.google.com/dl/android/maven2'
TOOL_DIRS = re.compile(r'^src/third_party/(android_build_tools/[^/]+|kotlinc|jdk|android_sdk|r8|'
                       r'android_toolchain|turbine|byte_buddy|bazel|android_platform|robolectric)')
# CIPD dir -> (Maven group:artifact[:classifier], file inside the CIPD dir to compare,
#              file inside the Maven jar to compare, or None to compare the jar itself)
MAVEN = {
    'android_build_tools/aapt2': ('com.android.tools.build:aapt2:linux', 'aapt2', 'aapt2'),
    'android_build_tools/bundletool': ('com.android.tools.build:bundletool', 'bundletool.jar', None),
    'android_build_tools/manifest_merger': ('com.android.tools.build:manifest-merger', 'manifest-merger.jar', None),
}


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'android-tools/1.0'}),
                                    timeout=120) as r:
            return r.read()
    except Exception:
        return None


def deps_packages(src):
    text = open(os.path.join(src, 'DEPS')).read()
    scope = {'Var': lambda n: '{%s}' % n, 'Str': str, 'True': True, 'False': False}
    exec(text, scope)
    vars_ = scope.get('vars', {})
    out = []
    for path, d in scope.get('deps', {}).items():
        if not isinstance(d, dict) or d.get('dep_type') != 'cipd' or not TOOL_DIRS.match(path):
            continue
        for p in d.get('packages', []):
            pkg = p['package'].replace('${{platform}}', 'linux-amd64')
            ver = re.sub(r'\{(\w+)\}', lambda m: str(vars_.get(m[1], m[0])), p['version'])
            out.append((path[len('src/'):], pkg, ver))
    return out


def cipd_tags(pkg, ver):
    r = subprocess.run(['cipd', 'describe', pkg, '-version', ver], capture_output=True, text=True)
    tags = re.findall(r'^\s+(version:\S+|git_revision:\S+|3pp_ecosystem_hash:\S+)', r.stdout, re.M)
    return [t for t in tags if not t.startswith('3pp_ecosystem_hash')] or [ver[:12]]


def maven_check(cipd_dir, tool, tags, src):
    coord, local, inner = MAVEN[tool]
    parts = coord.split(':')
    g, a = parts[0], parts[1]
    cls = parts[2] if len(parts) > 2 else None
    vers = [re.sub(r'^version:\d+@', '', t) for t in tags if t.startswith('version:')]
    if not vers:
        return 'no version tag', ''
    v = re.sub(r'\.cr\d+$', '', vers[0])
    jar = get(f"{GOOGLE}/{g.replace('.', '/')}/{a}/{v}/{a}-{v}{'-' + cls if cls else ''}.jar")
    if jar is None:
        return f'{v} not on Google Maven', v
    path = None
    for root, _, files in os.walk(os.path.join(src, cipd_dir)):
        if local in files:
            path = os.path.join(root, local)
            break
    if path is None:
        return f'{v} on Google Maven; {local} not found in CIPD dir', v
    data = open(path, 'rb').read()
    other = jar if inner is None else zipfile.ZipFile(io.BytesIO(jar)).read(inner)
    same = hashlib.sha256(data).digest() == hashlib.sha256(other).digest()
    return (f'{v} on Google Maven, ' + ('identical' if same else 'different')), v


def main():
    src, inputs_file, out_dir = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    inputs = [l.strip()[6:] for l in open(inputs_file) if l.startswith('../../')]
    rows = []
    for path, pkg, ver in sorted(deps_packages(src)):
        tool = path[len('third_party/'):].removesuffix('/cipd')
        used = sum(1 for i in inputs if i.startswith(path + '/'))
        tags = cipd_tags(pkg, ver)
        maven, v = ('', '')
        if tool in MAVEN:
            maven, v = maven_check(path, tool, tags, src)
        rows.append({'path': path, 'pkg': pkg, 'tags': ' '.join(tags), 'used': used, 'maven': maven})
        print(path, pkg, tags, used, maven, flush=True)

    with open(os.path.join(out_dir, 'android-tools.tsv'), 'w') as f:
        f.write('path\tcipd_package\ttags\tbuild_inputs\tmaven\n')
        for r in rows:
            f.write(f"{r['path']}\t{r['pkg']}\t{r['tags']}\t{r['used']}\t{r['maven']}\n")
    lines = ['## Prebuilt Android build tools', '',
             f"{len(rows)} CIPD packages; {sum(1 for r in rows if r['used'])} have files the "
             'chrome_public_apk build graph reads (tools run by scripts may not show up as inputs).', '',
             '| directory | CIPD version | build inputs | Google Maven |', '|---|---|---:|---|']
    lines += [f"| `{r['path']}` | `{r['tags']}` | {r['used']} | {r['maven']} |" for r in rows]
    open(os.path.join(out_dir, 'android-tools.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
