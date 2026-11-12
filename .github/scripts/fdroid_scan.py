#!/usr/bin/env python3
"""Run fdroidserver's source scanner over a Chromium checkout and summarize
what it flags.

Usage: fdroid_scan.py <src dir> <output dir> [--rules scan-rules.txt]

With --rules, the scandelete paths in the file are applied the way F-Droid's
build server applies them: flagged files under those paths are deleted.

Writes findings.tsv (kind, path, bytes), summary.md and scanner.log.
"""

import argparse
import collections
import logging
import os
import re
import sys

from fdroidserver import common, metadata, scanner

FOUND = re.compile(r"^Found (?P<kind>.+?) at (?P<path>.+)$")


def group_of(path):
    parts = path.split('/')
    depth = 3 if parts[0] == 'third_party' and len(parts) > 3 else 2
    return '/'.join(parts[: min(depth, len(parts) - 1)]) or parts[0]


TOOLCHAIN_PREFIXES = (
    'build/linux/',
    'buildtools/',
    'third_party/android_build_tools/',
    'third_party/android_sdk/',
    'third_party/android_system_sdk/',
    'third_party/android_toolchain/',
    'third_party/aosp_dalvik/',
    'third_party/depot_tools/',
    'third_party/jdk/',
    'third_party/jdk11/',
    'third_party/kotlinc/',
    'third_party/llvm-build/',
    'third_party/llvm-libclang/',
    'third_party/ninja/',
    'third_party/node/',
    'third_party/r8/',
    'third_party/rust-toolchain/',
    'third_party/turbine/',
)
JAVA_PREFIXES = ('third_party/android_deps/', 'third_party/androidx/')
TEST_RE = re.compile(
    r'(^|/)(tests?|testdata|test_data|testing|fuzz|fuzzers?|corpus|'
    r'web_tests|perf_tests|webpagereplay|webgpu-cts|jetstream|speedometer|'
    r'benchmarks?|examples?|samples?|docs?)(/|$)|(^|/)net/data/|_test(data)?(/|$)'
)
CATEGORIES = (
    ('nonfree', 'Non-free dependency references (Play services, Firebase, ML Kit, unknown Maven repos)'),
    ('java', 'Prebuilt Java/Android libraries (androidx, android_deps)'),
    ('toolchain', 'Toolchains, SDKs and build tools'),
    ('test', 'Test, fuzzing, benchmark and example data'),
    ('other', 'Other'),
)


def category(kind, path):
    if kind.startswith('usual suspect') or kind.startswith('unknown maven repo'):
        return 'nonfree'
    p = path + '/'
    if p.startswith(JAVA_PREFIXES):
        return 'java'
    if p.startswith(TOOLCHAIN_PREFIXES):
        return 'toolchain'
    if TEST_RE.search(path):
        return 'test'
    return 'other'


def md(text):
    return text.replace('|', '\\|')


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024


def read_rules(path):
    rules = []
    with open(path) as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if line:
                rules.append(line)
    return rules


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('out')
    parser.add_argument('--rules')
    args = parser.parse_args()
    src, out = os.path.abspath(args.src), os.path.abspath(args.out)
    build = metadata.Build()
    if args.rules:
        build.scandelete = read_rules(os.path.abspath(args.rules))
    os.makedirs(out, exist_ok=True)
    logging.getLogger().setLevel(logging.ERROR)
    os.chdir(src)
    common.options = argparse.Namespace(json=True, verbose=False)
    store = scanner.MessageStore()
    problems = scanner.scan_source(src, build=build, json_per_build=store)
    with open(os.path.join(out, 'scanner.log'), 'w') as log:
        for level in ('errors', 'warnings', 'infos'):
            for msg, path in getattr(store, level):
                log.write(f'{level}\t{msg}\n')

    records = []
    deleted = len(store.infos)
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
        f.write('category\tkind\tpath\tbytes\n')
        for r in rows:
            f.write(f'{category(r[0], r[1])}\t{r[0]}\t{r[1]}\t{r[2]}\n')

    by_cat = collections.Counter()
    cat_size = collections.Counter()
    other_groups = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for kind, path, size in rows:
        c = category(kind, path)
        by_cat[c] += 1
        cat_size[c] += size
        if c == 'other':
            g = other_groups[group_of(path)]
            g[0] += 1
            g[1] += size
            g[2][kind] += 1

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
        f'{len(build.scandelete)} scandelete rules applied, {deleted} files deleted.'
        if args.rules
        else 'No scandelete rules applied.',
        '',
        '| category | count | size |',
        '|---|---:|---:|',
    ]
    for c, title in CATEGORIES:
        lines.append(f'| {title} | {by_cat[c]} | {human(cat_size[c])} |')
    lines += [
        '',
        '### "Other" by directory (top 60 by count)',
        '',
        '| directory | count | size | kinds |',
        '|---|---:|---:|---|',
    ]
    for name, (n, size, kinds) in sorted(other_groups.items(), key=lambda kv: -kv[1][0])[:60]:
        k = ', '.join(f'{md(x)} {c}' for x, c in kinds.most_common(3))
        lines.append(f'| `{name}` | {n} | {human(size)} | {k} |')
    lines += [
        '',
        '### By kind',
        '',
        '| kind | count | size |',
        '|---|---:|---:|',
    ]
    for kind, n in by_kind.most_common():
        lines.append(f'| {md(kind)} | {n} | {human(kind_size[kind])} |')
    lines += [
        '',
        '### All findings by directory (top 60 by count)',
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
