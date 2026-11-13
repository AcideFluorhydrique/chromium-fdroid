#!/usr/bin/env python3
"""Summarize the Java compile errors in a ninja log (#6).

Usage: java_errors.py <ninja log> <title> <output .md>

Groups javac/turbine errors by the missing package or symbol and lists the
source files that need changes.
"""

import collections
import os
import re
import sys

ERROR = re.compile(r'^(?:\.\./\.\./)?([^\s:]+\.(?:java|kt)):(\d+): error: (.+)$')
SYMBOL = re.compile(r'^\s+symbol:\s+(?:class|variable|method|interface)\s+(\S+)')
PACKAGE = re.compile(r'package (\S+) does not exist')
FAILED = re.compile(r'^FAILED: (.+)$')


def main():
    log, title, out = sys.argv[1:4]
    lines = open(log, errors='replace').read().splitlines()
    errors = []
    failed = []
    for i, line in enumerate(lines):
        m = FAILED.match(line)
        if m:
            failed.append(m[1].split()[0])
        m = ERROR.match(line)
        if not m:
            continue
        path, msg = m[1], m[3]
        what = msg
        p = PACKAGE.search(msg)
        if p:
            what = f'package {p[1]}'
        elif 'cannot find symbol' in msg:
            for nxt in lines[i + 1:i + 4]:
                s = SYMBOL.match(nxt)
                if s:
                    what = f'symbol {s[1]}'
                    break
        errors.append((path, what))

    by_what = collections.Counter(w for _, w in errors)
    files = collections.Counter(p for p, _ in errors)
    dirs = collections.Counter(os.path.dirname(p).split('/java/src/')[0] for p in files)

    md = [
        f'## Java compile: {title}',
        '',
        f'- failed build steps: {len(failed)}',
        f'- errors: {len(errors)} in {len(files)} files '
        '(javac stops after 100 errors per target, so this is a lower bound)',
        '',
    ]
    if errors:
        md += ['### Missing packages and symbols', '', '| what | errors |', '|---|---:|']
        md += [f'| `{w}` | {n} |' for w, n in by_what.most_common(60)]
        md += ['', '### Files with errors, by directory', '', '| directory | files |', '|---|---:|']
        md += [f'| `{d}` | {n} |' for d, n in dirs.most_common(60)]
        md += ['', '<details><summary>All files</summary>', '']
        md += [f'- `{p}` ({n})' for p, n in sorted(files.items())]
        md += ['', '</details>']
    if failed:
        md += ['', '### Failed steps', '']
        md += [f'- `{f}`' for f in failed[:40]]
    text = '\n'.join(md) + '\n'
    with open(out, 'w') as f:
        f.write(text)
    print(text)
    step = os.environ.get('GITHUB_STEP_SUMMARY')
    if step:
        with open(step, 'a') as f:
            f.write(text)


if __name__ == '__main__':
    main()
