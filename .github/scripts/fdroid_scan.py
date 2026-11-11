#!/usr/bin/env python3
"""Run fdroidserver's source scanner over a Chromium checkout and summarize
what it flags.

Usage: fdroid_scan.py <src dir> <output dir>

Writes findings.tsv (kind, path, bytes), summary.md and scanner.log.
"""

import argparse
import collections
import logging
import os
import re
import sys

from fdroidserver import common, scanner

FOUND = re.compile(r"^Found (?P<kind>.+?) at (?P<path>.+)$")


def group_of(path):
    parts = path.split('/')
    depth = 3 if parts[0] == 'third_party' and len(parts) > 3 else 2
    return '/'.join(parts[: min(depth, len(parts) - 1)]) or parts[0]


def md(text):
    return text.replace('|', '\\|')


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024


def main():
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    logging.getLogger().setLevel(logging.ERROR)
    os.chdir(src)
    common.options = argparse.Namespace(json=True, verbose=False)
    store = scanner.MessageStore()
    problems = scanner.scan_source('.', json_per_build=store)
    with open(os.path.join(out, 'scanner.log'), 'w') as log:
        for level in ('errors', 'warnings', 'infos'):
            for msg, path in getattr(store, level):
                log.write(f'{level}\t{msg}\n')

    records = []
    for msg, path in store.errors + store.warnings:
        m = FOUND.match(msg)
        records.append((m['kind'] if m else msg, path))

    rows = []
    for kind, path in records:
        path = os.path.normpath(path)
        try:
            size = os.lstat(path).st_size
        except OSError:
            size = 0
        rows.append((kind, path, size))
    rows.sort(key=lambda r: r[1])
    with open(os.path.join(out, 'findings.tsv'), 'w') as f:
        f.write('kind\tpath\tbytes\n')
        for r in rows:
            f.write(f'{r[0]}\t{r[1]}\t{r[2]}\n')

    by_kind = collections.Counter()
    kind_size = collections.Counter()
    by_group = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for kind, path, size in rows:
        by_kind[kind] += 1
        kind_size[kind] += size
        g = by_group[group_of(path)]
        g[0] += 1
        g[1] += size
        g[2][kind] += 1

    lines = [
        f'## fdroid scanner: {len(rows)} findings ({problems} problems reported)',
        '',
        '| kind | count | size |',
        '|---|---:|---:|',
    ]
    for kind, n in by_kind.most_common():
        lines.append(f'| {md(kind)} | {n} | {human(kind_size[kind])} |')
    lines += [
        '',
        '### By directory (top 60 by count)',
        '',
        '| directory | count | size | kinds |',
        '|---|---:|---:|---|',
    ]
    for name, (n, size, kinds) in sorted(by_group.items(), key=lambda kv: -kv[1][0])[:60]:
        k = ', '.join(f'{md(x)} {c}' for x, c in kinds.most_common(3))
        lines.append(f'| `{name}` | {n} | {human(size)} | {k} |')
    summary = '\n'.join(lines) + '\n'
    with open(os.path.join(out, 'summary.md'), 'w') as f:
        f.write(summary)
    print(summary)
    step = os.environ.get('GITHUB_STEP_SUMMARY')
    if step:
        with open(step, 'a') as f:
            f.write(summary)


if __name__ == '__main__':
    main()
