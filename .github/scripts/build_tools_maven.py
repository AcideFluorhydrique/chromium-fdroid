#!/usr/bin/env python3
"""Replace prebuilt Android build tools from CIPD with released versions from
Maven (accepted on fdroiddata#3911 instead of building them from source).

Used by gms_variant.py:  tools=r8,turbine   or   tools=r8:9.6.1,turbine:1.17.0

  r8       third_party/r8/cipd/lib/r8.jar <- com.android.tools:r8 on Google
           Maven. Chromium rolls R8 to the tip of R8's newest release branch,
           so the same version is used if it is published, else the newest of
           the same major.minor, else the newest one. custom_d8.jar and
           custom_r8.jar (prebuilt jars checked into Chromium) are rebuilt from
           their Java sources against that r8.jar, and the GraalVM native-image
           cipd/bin/custom_d8 is no longer used (dex.py runs the jar instead).
  turbine  third_party/turbine/cipd/turbine.jar <- com.google.turbine:turbine
           (the all-deps jar) on Maven Central, newest release unless a
           version is given. The GraalVM native-image cipd/turbine is no longer
           used.

Every download is printed with its sha256.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

GOOGLE = 'https://dl.google.com/dl/android/maven2'
CENTRAL = 'https://repo1.maven.org/maven2'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'build-tools-maven/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def versions(repo, group, name):
    meta = fetch(f"{repo}/{group.replace('.', '/')}/{name}/maven-metadata.xml").decode()
    return re.findall(r'<version>([^<]+)</version>', meta)


def overwrite(path, data):
    # CIPD installs its files read-only (and may hard-link them from its cache).
    d = os.path.dirname(path)
    os.chmod(d, 0o755)
    if os.path.lexists(path):
        os.chmod(path, 0o644)
        os.unlink(path)
    with open(path, 'wb') as f:
        f.write(data)


def remove(path):
    if os.path.lexists(path):
        os.chmod(os.path.dirname(path), 0o755)
        os.unlink(path)


def sub_once(path, pattern, repl, flags=re.M):
    s = open(path).read()
    new, n = re.subn(pattern, repl, s, flags=flags)
    if n != 1:
        sys.exit(f'{path}: expected one match of {pattern!r}, found {n}')
    with open(path, 'w') as f:
        f.write(new)


def pick_r8(current, available):
    """Same version, else newest of the same major.minor, else newest."""
    if current in available:
        return current, 'same version'
    m = re.match(r'(\d+\.\d+)\.', current or '')
    if m:
        same = [v for v in available if v.startswith(m[1] + '.')]
        if same:
            return same[-1], f'newest {m[1]}.x release'
    return available[-1], 'newest release (no release of the same major.minor)'


def jar_from_dir(classes_dir, out_jar):
    names = sorted(os.path.relpath(os.path.join(r, f), classes_dir)
                   for r, _, fs in os.walk(classes_dir) for f in fs)
    tmp = out_jar + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in names:
            info = zipfile.ZipInfo(n, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(os.path.join(classes_dir, n), 'rb') as f:
                z.writestr(info, f.read())
    os.replace(tmp, out_jar)


def swap_r8(src, version=None):
    jdk = os.path.join(src, 'third_party/jdk/current/bin')
    r8 = os.path.join(src, 'third_party/r8/cipd/lib/r8.jar')
    out = subprocess.run([os.path.join(jdk, 'java'), '-cp', r8, 'com.android.tools.r8.R8', '--version'],
                         capture_output=True, text=True).stdout.strip()
    current = (re.search(r'R8 (\S+)', out) or [None, None])[1]
    print(f'r8: Chromium ships {out.splitlines()[0] if out else "?"} '
          f'(sha256 {hashlib.sha256(open(r8, "rb").read()).hexdigest()[:16]})', file=sys.stderr)
    available = versions(GOOGLE, 'com.android.tools', 'r8')
    if version:
        why = 'given'
        if version not in available:
            sys.exit(f'r8 {version} is not on Google Maven; newest: {" ".join(available[-8:])}')
    else:
        version, why = pick_r8(current, available)
    data = fetch(f'{GOOGLE}/com/android/tools/r8/{version}/r8-{version}.jar')
    print(f'r8: com.android.tools:r8:{version} from Google Maven ({why}), '
          f'{len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}', file=sys.stderr)
    overwrite(r8, data)

    # custom_d8.jar / custom_r8.jar: small wrappers checked into Chromium as
    # jars; build them from their sources against the r8.jar now in place.
    for name, cls in (('custom_d8', 'CustomD8'), ('custom_r8', 'CustomR8')):
        tmp = tempfile.mkdtemp()
        java = os.path.join(src, f'third_party/r8/java/src/org/chromium/build/{cls}.java')
        subprocess.run([os.path.join(jdk, 'javac'), '-nowarn', '-cp', r8, '-d', tmp, java], check=True)
        jar_from_dir(tmp, os.path.join(src, f'third_party/r8/{name}.jar'))
        shutil.rmtree(tmp)
        print(f'r8: rebuilt third_party/r8/{name}.jar from {cls}.java', file=sys.stderr)

    # The native-image custom_d8 was built from Google's r8.jar: run the jar.
    sub_once(os.path.join(src, 'build/android/gyp/dex.py'),
             r"use_custom_d8_binary = \(\n\s+not options\.skip_custom_d8\n\s+and sys\.platform == 'linux'\n"
             r"\s+and platform\.machine\(\) == 'x86_64'\n\s+\)",
             'use_custom_d8_binary = False')
    sub_once(os.path.join(src, 'build/config/android/internal_rules.gni'),
             r'^\s*_custom_d8_binary_path,\n', '')
    sub_once(os.path.join(src, 'build/config/android/internal_rules.gni'),
             r'^_custom_d8_binary_path = .*\n', '')
    remove(os.path.join(src, 'third_party/r8/cipd/bin/custom_d8'))
    print('r8: dex.py runs CustomD8 from the jars; removed cipd/bin/custom_d8', file=sys.stderr)


def swap_turbine(src, version=None):
    available = versions(CENTRAL, 'com.google.turbine', 'turbine')
    if version and version not in available:
        sys.exit(f'turbine {version} is not on Maven Central; newest: {" ".join(available[-8:])}')
    version = version or available[-1]
    data = fetch(f'{CENTRAL}/com/google/turbine/turbine/{version}/turbine-{version}-all-deps.jar')
    print(f'turbine: com.google.turbine:turbine:{version} (all-deps) from Maven Central, '
          f'{len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}', file=sys.stderr)
    overwrite(os.path.join(src, 'third_party/turbine/cipd/turbine.jar'), data)
    # Always use the jar, never the native-image binary.
    sub_once(os.path.join(src, 'build/config/android/internal_rules.gni'),
             r'_use_turbine_binary = host_os == "linux" && host_cpu == "x64" &&',
             '_use_turbine_binary = false &&')
    remove(os.path.join(src, 'third_party/turbine/cipd/turbine'))
    print('turbine: internal_rules.gni uses turbine.jar; removed cipd/turbine', file=sys.stderr)


def apply(src, value):
    for item in value.split(','):
        name, _, version = item.partition(':')
        if name == 'r8':
            swap_r8(src, version or None)
        elif name == 'turbine':
            swap_turbine(src, version or None)
        else:
            sys.exit(f'unknown tool {name!r} (r8, turbine)')


if __name__ == '__main__':
    apply(sys.argv[1], sys.argv[2])
