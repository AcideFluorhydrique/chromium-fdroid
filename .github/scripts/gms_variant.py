#!/usr/bin/env python3
"""Replace or drop the non-free Java libraries in a Chromium checkout (#6).

Usage: gms_variant.py <src dir> <spec>

<spec> is a space-separated list of:
  gms=microg     Provide the Play services/Firebase targets from a new
                 //fdroid_gms directory: targets microG publishes a library for
                 (org.microg.gms on Maven Central) use it, the rest are empty.
  gms=drop       Same directory, but every target is empty.
  drop=GROUPS    Turn the targets of these groups in
                 //third_party/android_deps into empty java_groups. Groups:
                 playcore, mlkit, impress. impress also removes the XR
                 feature module, which packages impress's and ARCore's native
                 libraries and is added regardless of enable_arcore/enable_vr.

google_play_services_package is not a GN build argument (it is set with
if (!defined(...)) in //build/config/android/config.gni), so gms=... edits
that file, as Cromite does. Nothing is printed for args.gn any more.
An empty java_group keeps GN happy, so javac then reports every place in
Chromium that still uses the removed library.
"""

import io
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

MAVEN = 'https://repo1.maven.org/maven2'
DROP_GROUPS = {
    'playcore': re.compile(r'^com_google_android_play_'),
    'mlkit': re.compile(r'mlkit'),
    'impress': re.compile(r'^com_google_ar_impress_java$'),
}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'gms-variant/1.0'})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 5:
                raise
        except urllib.error.URLError:
            if attempt == 5:
                raise
        time.sleep(10 * (attempt + 1))


def latest(group, artifact):
    meta = fetch(f"{MAVEN}/{group.replace('.', '/')}/{artifact}/maven-metadata.xml")
    root = ET.fromstring(meta)
    v = root.findtext('versioning/release') or root.findtext('versioning/latest')
    return v


def microg_jars(artifacts, out_jar):
    """Download the microG libraries and their org.microg dependencies and
    merge their classes into one jar."""
    seen = {}
    todo = [('org.microg.gms', a, None) for a in artifacts]
    while todo:
        group, artifact, version = todo.pop()
        if (group, artifact) in seen:
            continue
        version = version or latest(group, artifact)
        base = f"{MAVEN}/{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}"
        pom = ET.fromstring(fetch(base + '.pom'))
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        packaging = pom.findtext('m:packaging', 'jar', ns)
        data = fetch(base + ('.aar' if packaging == 'aar' else '.jar'))
        seen[(group, artifact)] = (version, packaging, data)
        for dep in pom.findall('m:dependencies/m:dependency', ns):
            g = dep.findtext('m:groupId', '', ns)
            if g.startswith('org.microg') and dep.findtext('m:scope', 'compile', ns) in ('compile', 'runtime'):
                todo.append((g, dep.findtext('m:artifactId', '', ns), dep.findtext('m:version', None, ns)))

    names = set()
    with zipfile.ZipFile(out_jar, 'w', zipfile.ZIP_DEFLATED) as out:
        for (group, artifact), (version, packaging, data) in sorted(seen.items()):
            print(f'microG: {group}:{artifact}:{version} ({packaging})', file=sys.stderr)
            jars = []
            if packaging == 'aar':
                aar = zipfile.ZipFile(io.BytesIO(data))
                jars = [aar.read(n) for n in aar.namelist()
                        if n == 'classes.jar' or (n.startswith('libs/') and n.endswith('.jar'))]
            else:
                jars = [data]
            for j in jars:
                z = zipfile.ZipFile(io.BytesIO(j))
                for n in z.namelist():
                    if n.endswith('.class') and n not in names:
                        names.add(n)
                        out.writestr(n, z.read(n))
    return sorted(f'{g}:{a}:{v[0]}' for (g, a), v in seen.items())


def referenced_gms_targets(src):
    names = set()
    pat = re.compile(r'\$google_play_services_package:([a-z0-9_]+)')
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ('.git', 'out')]
        for f in files:
            if f.endswith(('.gn', '.gni')):
                try:
                    with open(os.path.join(root, f), errors='ignore') as fh:
                        names.update(pat.findall(fh.read()))
                except OSError:
                    pass
    return sorted(names)


def write_gms_dir(src, mode):
    names = referenced_gms_targets(src)
    d = os.path.join(src, 'fdroid_gms')
    os.makedirs(d, exist_ok=True)
    lines = ['import("//build/config/android/rules.gni")', '']
    provided = []
    if mode == 'microg':
        index = fetch(f'{MAVEN}/org/microg/gms/').decode()
        available = set(re.findall(r'href="([a-z0-9\-]+)/"', index))
        wanted = {}
        for n in names:
            m = re.match(r'^google_play_services_(.+)_java$', n)
            if m and 'play-services-' + m[1].replace('_', '-') in available:
                wanted[n] = 'play-services-' + m[1].replace('_', '-')
        provided = microg_jars(sorted(set(wanted.values())), os.path.join(d, 'microg.jar'))
        lines += [
            'java_prebuilt("microg_java") {',
            '  jar_path = "microg.jar"',
            '  supports_android = true',
            '  enable_bytecode_checks = false',
            '}',
            '',
        ]
    else:
        wanted = {}
    for n in names:
        if n in wanted:
            lines += [f'java_group("{n}") {{', '  deps = [ ":microg_java" ]', '}', '']
        else:
            lines += [f'java_group("{n}") {{', '  deps = []', '}', '']
    with open(os.path.join(d, 'BUILD.gn'), 'w') as f:
        f.write('\n'.join(lines))
    print(f'fdroid_gms: {len(wanted)} targets from microG, '
          f'{len(names) - len(wanted)} empty', file=sys.stderr)
    for p in provided:
        print('  ' + p, file=sys.stderr)


def drop_android_deps(src, groups):
    path = os.path.join(src, 'third_party/android_deps/BUILD.gn')
    s = open(path).read()
    target = re.compile(r'\b(android_aar_prebuilt|java_prebuilt|java_group|android_library)\("([a-z0-9_]+)"\)\s*\{')
    out, pos, dropped = [], 0, []
    for m in target.finditer(s):
        if m.start() < pos:
            continue
        name = m[2]
        if not any(DROP_GROUPS[g].search(name) for g in groups):
            continue
        depth, i = 0, m.end() - 1
        while True:
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append(s[pos:m.start()])
        out.append(f'java_group("{name}") {{\n    deps = []\n  }}')
        pos = i + 1
        dropped.append(name)
    out.append(s[pos:])
    with open(path, 'w') as f:
        f.write(''.join(out))
    print(f'android_deps: dropped {len(dropped)} targets: {" ".join(dropped)}', file=sys.stderr)


def drop_xr_module(src):
    path = os.path.join(src, 'chrome/android/modules/chrome_feature_modules.gni')
    s = open(path).read()
    new = re.sub(r'^\s*xr_module_desc,\n', '', s, count=1, flags=re.M)
    if new == s:
        sys.exit(f'{path}: xr_module_desc not found in chrome_module_descs')
    with open(path, 'w') as f:
        f.write(new)
    print('chrome_feature_modules.gni: removed the XR feature module', file=sys.stderr)


def set_gms_package(src):
    path = os.path.join(src, 'build/config/android/config.gni')
    s = open(path).read()
    old = 'google_play_services_package = "//third_party/android_deps"'
    if s.count(old) != 1:
        sys.exit(f'{path}: default google_play_services_package not found')
    with open(path, 'w') as f:
        f.write(s.replace(old, 'google_play_services_package = "//fdroid_gms"'))
    print('config.gni: google_play_services_package = //fdroid_gms', file=sys.stderr)


def main():
    src, spec = sys.argv[1], sys.argv[2].split()
    args = []
    for item in spec:
        key, _, value = item.partition('=')
        if key == 'gms':
            assert value in ('microg', 'drop'), item
            write_gms_dir(src, value)
            set_gms_package(src)
        elif key == 'drop':
            groups = value.split(',')
            assert all(g in DROP_GROUPS for g in groups), item
            drop_android_deps(src, groups)
            if 'impress' in groups:
                drop_xr_module(src)
        else:
            sys.exit(f'unknown spec item {item}')
    print('\n'.join(args))


if __name__ == '__main__':
    main()
