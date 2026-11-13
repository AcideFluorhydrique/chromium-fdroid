#!/usr/bin/env python3
"""Report the prebuilt Java libraries that chrome_public_apk uses (#5, #6).

Usage: deps_report.py <src dir> <out dir in src> <build-inputs.txt> <output dir>

For every artifact in third_party/android_deps and third_party/androidx whose
files are inputs of the chrome_public_apk build graph:
  - its Maven coordinates (from bill_of_materials.json),
  - whether that exact version is on Maven Central or Google Maven,
  - for non-free artifacts, the GN dependency chain that pulls it in.

Writes deps.md and deps.tsv.
"""

import collections
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

REPOS = {
    'google': 'https://dl.google.com/dl/android/maven2',
    'central': 'https://repo1.maven.org/maven2',
}
NONFREE = (
    re.compile(r'^com\.google\.android\.gms'),
    re.compile(r'^com\.google\.firebase'),
    re.compile(r'^com\.google\.mlkit'),
    re.compile(r'^com\.google\.android\.play'),
    re.compile(r'^com\.google\.ar'),
    re.compile(r'^com\.google\.android\.libraries\.identity\.googleid'),
    re.compile(r'^androidx\.credentials:credentials-play-services'),
)
LIB_DIR = re.compile(r'^third_party/(android_deps|androidx)/cipd/libs/([^/]+)/')


def dir_name(group, name):
    return re.sub(r'[.\-]', '_', f'{group}_{name}')


def exists(url):
    req = urllib.request.Request(url, method='HEAD')
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
        except Exception:
            pass
    return None


def where(group, name, version):
    found = []
    for repo, base in REPOS.items():
        url = f"{base}/{group.replace('.', '/')}/{name}/{version}/{name}-{version}.pom"
        r = exists(url)
        if r:
            found.append(repo)
        elif r is None:
            found.append(f'{repo}?')
    return found


def gn_path(src, out, target):
    gn = os.path.join(src, 'buildtools/linux64/gn')
    r = subprocess.run(
        [gn, 'path', out, '//chrome/android:chrome_public_apk', target],
        cwd=src, capture_output=True, text=True,
    )
    chain = [l.split(' --[')[0].strip() for l in r.stdout.splitlines()
             if l.startswith('//')]
    return chain


def gn_owner(src, out, path):
    """The GN target whose sources/inputs include `path`."""
    gn = os.path.join(src, 'buildtools/linux64/gn')
    r = subprocess.run(
        [gn, 'refs', out, '//' + path], cwd=src, capture_output=True, text=True,
    )
    targets = [t for t in r.stdout.split() if t.startswith('//')]
    return next((t for t in targets if t.endswith('_java')), targets[0] if targets else '')


def main():
    src, out, inputs_file, report_dir = sys.argv[1:5]
    os.makedirs(report_dir, exist_ok=True)

    used = collections.defaultdict(dict)
    with open(inputs_file) as f:
        for line in f:
            p = line.strip()
            if p.startswith('../../'):
                m = LIB_DIR.match(p[len('../../'):])
                if m:
                    used[m[1]].setdefault(m[2], p[len('../../'):])

    rows = []
    for gn_dir in ('android_deps', 'androidx'):
        with open(os.path.join(src, 'third_party', gn_dir, 'bill_of_materials.json')) as f:
            bom = json.load(f)
        for e in bom:
            d = dir_name(e['group'], e['name'])
            if d not in used[gn_dir]:
                continue
            coord = f"{e['group']}:{e['name']}"
            nonfree = any(r.search(coord) for r in NONFREE)
            target = gn_owner(src, out, used[gn_dir][d]) if nonfree else ''
            rows.append({
                'dir': gn_dir, 'group': e['group'], 'name': e['name'],
                'version': e['version'], 'nonfree': nonfree, 'target': target,
            })

    with concurrent.futures.ThreadPoolExecutor(16) as pool:
        for row, found in zip(rows, pool.map(
                lambda r: where(r['group'], r['name'], r['version']), rows)):
            row['found'] = found
    for row in rows:
        row['chain'] = gn_path(src, out, row['target']) if row['nonfree'] and row['target'] else []

    with open(os.path.join(report_dir, 'deps.tsv'), 'w') as f:
        f.write('dir\tgroup\tname\tversion\tnonfree\tfound_in\ttarget\n')
        for r in rows:
            f.write(f"{r['dir']}\t{r['group']}\t{r['name']}\t{r['version']}\t"
                    f"{'yes' if r['nonfree'] else 'no'}\t{','.join(r['found']) or '-'}\t{r['target']}\n")

    def count(pred):
        return sum(1 for r in rows if pred(r))

    lines = [
        '## Prebuilt Java libraries in the chrome_public_apk build graph',
        '',
        '| | android_deps | androidx |',
        '|---|---:|---:|',
    ]
    for label, pred in (
        ('in build graph', lambda r: True),
        ('exact version on Google Maven or Maven Central', lambda r: any(x in ('google', 'central') for x in r['found'])),
        ('not found (e.g. androidx snapshots)', lambda r: not any(x in ('google', 'central') for x in r['found'])),
        ('non-free', lambda r: r['nonfree']),
    ):
        lines.append(f"| {label} | {count(lambda r: r['dir'] == 'android_deps' and pred(r))} "
                     f"| {count(lambda r: r['dir'] == 'androidx' and pred(r))} |")

    lines += ['', '### Non-free artifacts and why they are in the build', '']
    for r in rows:
        if r['nonfree']:
            lines.append(f"- `{r['group']}:{r['name']}:{r['version']}`")
            if r['chain']:
                lines.append('  ' + ' → '.join(f'`{c}`' for c in r['chain']))
            else:
                lines.append('  (no GN path found)')

    lines += ['', '### Not found on Google Maven or Maven Central', '',
              '| artifact | version |', '|---|---|']
    for r in rows:
        if not any(x in ('google', 'central') for x in r['found']):
            lines.append(f"| `{r['group']}:{r['name']}` | {r['version']} |")

    text = '\n'.join(lines) + '\n'
    with open(os.path.join(report_dir, 'deps.md'), 'w') as f:
        f.write(text)
    print(text)
    step = os.environ.get('GITHUB_STEP_SUMMARY')
    if step:
        with open(step, 'a') as f:
            f.write(text)


if __name__ == '__main__':
    main()
