#!/usr/bin/env python3
"""Check that Chromium's CIPD copies of Java libraries are the Maven files.

Usage: maven_verify.py <src dir> <build-inputs.txt> <output dir>

For every android_deps/androidx library that chrome_public_apk reads, the
.aar/.jar under cipd/libs/ is compared with the same version on Google Maven
and Maven Central: byte-identical (same sha256), same contents (same entries
and CRCs, repacked), different, or not on Maven. If they are identical, an
F-Droid recipe can fetch them from Maven by version and checksum instead.

Writes maven-verify.md and maven-verify.tsv.
"""

import collections
import concurrent.futures
import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile

REPOS = {
    'google': 'https://dl.google.com/dl/android/maven2',
    'central': 'https://repo1.maven.org/maven2',
}
LIB_DIR = re.compile(r'^third_party/(android_deps|androidx)/cipd/libs/([^/]+)/')


def dir_name(group, name):
    return re.sub(r'[.\-]', '_', f'{group}_{name}')


def get(url):
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'maven-verify/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
    return None


def entries(data):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        return {i.filename: i.CRC for i in z.infolist() if not i.is_dir()}
    except zipfile.BadZipFile:
        return None


def check(row):
    local = row['local']
    ext = os.path.splitext(local)[1]
    data = open(local, 'rb').read()
    row['sha256'] = hashlib.sha256(data).hexdigest()
    g, n, v = row['group'], row['name'], row['version']
    for repo, base in REPOS.items():
        remote = get(f"{base}/{g.replace('.', '/')}/{n}/{v}/{n}-{v}{ext}")
        if remote is None:
            continue
        if hashlib.sha256(remote).digest() == hashlib.sha256(data).digest():
            return repo, 'identical'
        a, b = entries(data), entries(remote)
        if a is not None and a == b:
            return repo, 'same contents'
        if a is not None and b is not None:
            only_l = sorted(set(a) - set(b))
            only_r = sorted(set(b) - set(a))
            changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
            row['diff'] = (f'{len(changed)} changed, {len(only_l)} only in CIPD, '
                           f'{len(only_r)} only on Maven; e.g. {(changed + only_l + only_r)[:3]}')
        return repo, 'different'
    if SNAPSHOT_REPO and v.endswith('-SNAPSHOT'):
        vdir = f"{SNAPSHOT_REPO}/{g.replace('.', '/')}/{n}/{v}"
        remote = get(f"{vdir}/{n}-{v}{ext}")
        if remote is None:
            # Snapshot repositories usually name files with a timestamp, listed in
            # maven-metadata.xml as <snapshotVersion><extension/><value/>.
            meta = get(f"{vdir}/maven-metadata.xml")
            if meta:
                vals = re.findall(r'<snapshotVersion>\s*(?:<classifier>[^<]*</classifier>\s*)?'
                                  rf'<extension>{ext[1:]}</extension>\s*<value>([^<]+)</value>', meta.decode())
                if vals:
                    remote = get(f"{vdir}/{n}-{vals[-1]}{ext}")
                row['diff'] = f'metadata: {len(vals)} {ext[1:]} snapshot(s)'
            else:
                row['diff'] = f'no {vdir}/maven-metadata.xml'
        row['release'] = latest_release(g, n)
        if remote is not None:
            same = hashlib.sha256(remote).digest() == hashlib.sha256(data).digest()
            if not same and entries(data) is not None and entries(data) == entries(remote):
                return 'androidx.dev', 'snapshot, same contents'
            return 'androidx.dev', 'snapshot, identical' if same else 'snapshot, different'
    return '', 'not on Maven'


SNAPSHOT_REPO = None


def latest_release(g, n):
    meta = get(f"{REPOS['google']}/{g.replace('.', '/')}/{n}/maven-metadata.xml")
    if not meta:
        return ''
    vs = re.findall(r'<version>([^<]+)</version>', meta.decode())
    stable = [v for v in vs if re.fullmatch(r'[0-9.]+', v)]
    return (stable or vs or [''])[-1] + ('' if stable else ' (pre-release)')


def main():
    src, inputs_file, out_dir = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    global SNAPSHOT_REPO
    m = re.search(r"https://androidx\.dev/snapshots/builds/\d+/artifacts/repository",
                  open(os.path.join(src, 'third_party/androidx/build.gradle')).read())
    SNAPSHOT_REPO = m[0] if m else None
    used = collections.defaultdict(set)
    for line in open(inputs_file):
        p = line.strip()
        if p.startswith('../../'):
            m = LIB_DIR.match(p[6:])
            if m:
                used[m[1]].add(m[2])

    rows = []
    for gn_dir in ('android_deps', 'androidx'):
        bom = json.load(open(os.path.join(src, 'third_party', gn_dir, 'bill_of_materials.json')))
        for e in bom:
            d = dir_name(e['group'], e['name'])
            if d not in used[gn_dir]:
                continue
            libdir = os.path.join(src, 'third_party', gn_dir, 'cipd', 'libs', d)
            files = sorted(f for f in os.listdir(libdir) if f.endswith(('.aar', '.jar')))
            for f in files:
                rows.append({'dir': gn_dir, 'group': e['group'], 'name': e['name'],
                             'version': e['version'], 'file': f, 'local': os.path.join(libdir, f)})

    with concurrent.futures.ThreadPoolExecutor(16) as pool:
        for row, (repo, status) in zip(rows, pool.map(check, rows)):
            row['repo'], row['status'] = repo, status

    with open(os.path.join(out_dir, 'maven-verify.tsv'), 'w') as f:
        f.write('dir\tgroup\tname\tversion\tfile\tstatus\trepo\trelease\tsha256\tdiff\n')
        for r in rows:
            f.write(f"{r['dir']}\t{r['group']}\t{r['name']}\t{r['version']}\t{r['file']}\t"
                    f"{r['status']}\t{r['repo']}\t{r.get('release', '')}\t{r['sha256']}\t{r.get('diff', '')}\n")

    counts = collections.Counter(r['status'] for r in rows)
    lines = ['## CIPD Java libraries vs Maven', '',
             f'{len(rows)} files of {sum(len(v) for v in used.values())} libraries that chrome_public_apk reads.', '',
             '| result | files |', '|---|---:|']
    statuses = ('identical', 'same contents', 'different', 'snapshot, identical',
                'snapshot, same contents', 'snapshot, different', 'not on Maven')
    for s in statuses:
        lines.append(f'| {s} | {counts.get(s, 0)} |')
    if SNAPSHOT_REPO:
        lines += ['', f'Snapshots are compared with {SNAPSHOT_REPO}; "release" is the newest '
                  'version of that artifact on Google Maven.']
    for s in statuses[1:]:
        sel = [r for r in rows if r['status'] == s]
        if sel:
            lines += ['', f'### {s}', '', '| artifact | version | file | release | detail |',
                      '|---|---|---|---|---|']
            lines += [f"| `{r['group']}:{r['name']}` | {r['version']} | {r['file']} | "
                      f"{r.get('release', '')} | {r.get('diff', r['repo'])} |" for r in sel]
    open(os.path.join(out_dir, 'maven-verify.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:10]))


if __name__ == '__main__':
    main()
