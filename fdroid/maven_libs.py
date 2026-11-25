#!/usr/bin/env python3
"""Put third_party/androidx/cipd and third_party/android_deps/cipd together
from Google Maven and Maven Central.

Usage: maven_libs.py <chromium src dir> <cipd-pins.json>

prebuild does not sync these CIPD packages (fdroid/replaced-deps.txt). Which
files they hold comes from reports/<version>/cipd-pins.json (written by
sync-trim.yml); the Maven coordinates from the bill_of_materials.json next to
each BUILD.gn: libs/<group_name with . and - as _>/<name>.<ext> is
<group>:<name>:<version>@<ext>. Releases are fetched at their version;
snapshots (androidx builds Chromium takes from androidx.dev, not on Maven) at
the closest release on Google Maven, as gms_variant.py androidx=release does.
Prints how many files are byte-identical to the CIPD ones and which are on
neither Maven repository.
"""

import concurrent.futures
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

GOOGLE = 'https://dl.google.com/dl/android/maven2'
CENTRAL = 'https://repo1.maven.org/maven2'
PACKAGES = ('third_party/androidx', 'third_party/android_deps')
# Never fetched: Google's non-free libraries. The F-Droid variant replaces
# them (gms_variant.py: microG, stubs, drop=), so the build must not need
# their files; if it does, build.sh's dry run lists them as missing.
NONFREE = re.compile(r'^(com\.google\.android\.gms|com\.google\.firebase|com\.google\.android\.play'
                     r'|com\.google\.mlkit|com\.google\.ar|com\.google\.android\.datatransport'
                     r'|com\.google\.android\.libraries|com\.google\.android\.recaptcha)(\.|$)')


def fetch(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            err = e
        except OSError as e:
            err = e
        time.sleep(5 * (i + 1))
    raise err


_meta = {}


def versions(repo, group, name):
    key = (repo, group, name)
    if key not in _meta:
        try:
            meta = fetch(f"{repo}/{group.replace('.', '/')}/{name}/maven-metadata.xml").decode()
            _meta[key] = re.findall(r'<version>([^<]+)</version>', meta)
        except urllib.error.HTTPError:
            _meta[key] = []
    return _meta[key]


def release_for(version, available):
    """The snapshot's own version (stable or alpha/beta/rc), else the newest stable."""
    base = version[:-len('-SNAPSHOT')]
    same = [x for x in available if x == base or x.startswith(base + '-')]
    stable = [x for x in available if re.fullmatch(r'[0-9.]+', x)]
    return (same or stable or available or [None])[-1]


def coordinates(src):
    """libs dir name -> (group, name, version), from both bills of materials."""
    out = {}
    for pkg in PACKAGES:
        for e in json.load(open(os.path.join(src, pkg, 'bill_of_materials.json'))):
            d = re.sub(r'[.\-]', '_', f"{e['group']}_{e['name']}")
            out.setdefault((pkg, d), (e['group'], e['name'], e['version']))
    return out


def resolve(group, name, version):
    """(repo, version) to fetch, or (None, why)."""
    for repo in (GOOGLE, CENTRAL):
        available = versions(repo, group, name)
        if not available:
            continue
        if version.endswith('-SNAPSHOT'):
            rel = release_for(version, available)
            if rel:
                return repo, rel
        elif version in available:
            return repo, version
    return None, f'{group}:{name}:{version} is on neither Google Maven nor Maven Central'


def main():
    src, pins_path = sys.argv[1:3]
    pins = json.load(open(pins_path))['files']
    coords = coordinates(src)
    wanted = []
    unknown = []
    nonfree = []
    for rel, sha in pins.items():
        m = re.match(r'(third_party/(?:androidx|android_deps))/cipd/libs/([^/]+)/([^/]+)\.(aar|jar)$', rel)
        if not m:
            if any(rel.startswith(p + '/cipd/') for p in PACKAGES):
                unknown.append(rel)
            continue
        pkg, d, base, ext = m.groups()
        c = coords.get((pkg, d))
        if not c:
            unknown.append(rel)
            continue
        if NONFREE.match(c[0]):
            nonfree.append(f'{rel}: {c[0]}:{c[1]}')
            continue
        wanted.append((rel, sha, c, ext))

    def get(item):
        rel, sha, (group, name, version), ext = item
        repo, v = resolve(group, name, version)
        if not repo:
            return rel, None, v
        url = f"{repo}/{group.replace('.', '/')}/{name}/{v}/{name}-{v}.{ext}"
        try:
            data = fetch(url)
        except urllib.error.HTTPError as e:
            return rel, None, f'{url}: HTTP {e.code}'
        dst = os.path.join(src, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(data)
        same = hashlib.sha256(data).hexdigest() == sha
        where = 'Google Maven' if repo == GOOGLE else 'Maven Central'
        return rel, same, f'{group}:{name}:{v}' + ('' if v == version else f' (for {version})') + f' from {where}'

    identical, differ, failed = [], [], []
    with concurrent.futures.ThreadPoolExecutor(16) as pool:
        for rel, same, what in pool.map(get, wanted):
            (failed if same is None else identical if same else differ).append(f'{rel}: {what}')
    print(f'maven_libs: {len(identical)} files byte-identical to the CIPD ones, '
          f'{len(differ)} differ (snapshots or rebuilt), {len(failed)} not on Maven, '
          f'{len(unknown)} other CIPD files not reproduced, {len(nonfree)} non-free not fetched')
    for title, items in (('differ', differ), ('not on Maven', failed), ('not reproduced', unknown),
                         ('non-free, not fetched', nonfree)):
        for x in items:
            print(f'  {title}: {x}')
    # Not fatal here: the build graph decides whether a missing file matters
    # (ninja stops at a missing input; build.sh's dry run lists them all).


if __name__ == '__main__':
    main()
