#!/usr/bin/env python3
"""Remove DEPS entries from chromium/src/DEPS before gclient sync.

Usage: skip_deps.py <src/DEPS> <skip-deps.txt>

custom_deps = None in .gclient only skips git dependencies: gclient names a
CIPD dependency "<path>:<package>", so a custom_deps key with the path does
not match it, and CIPD and GCS packages are fetched whatever their URL
override says. Deleting the entries from the deps dict skips all three kinds.
Only the listed entries are cut out of the text; the rest of DEPS stays as it
is. Fails if an entry is not in DEPS, so a stale list is noticed.
"""

import ast
import sys


def main():
    deps_path, list_path = sys.argv[1:3]
    skip = [l.strip() for l in open(list_path)
            if l.strip() and not l.lstrip().startswith('#')]
    text = open(deps_path).read()
    tree = ast.parse(text)
    deps = next(n.value for n in tree.body
                if isinstance(n, ast.Assign) and len(n.targets) == 1
                and getattr(n.targets[0], 'id', None) == 'deps')

    lines = text.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))

    def offset(lineno, col):
        # ast columns are UTF-8 byte offsets; DEPS is ASCII.
        return starts[lineno - 1] + col

    found = {}
    for key, value in zip(deps.keys, deps.values):
        if isinstance(key, ast.Constant) and key.value in skip:
            found[key.value] = (offset(key.lineno, key.col_offset),
                                offset(value.end_lineno, value.end_col_offset),
                                getattr(value, 'keys', None) and next(
                                    (v.value for k, v in zip(value.keys, value.values)
                                     if getattr(k, 'value', None) == 'dep_type'), 'git') or 'git')
    missing = [s for s in skip if s not in found]
    if missing:
        sys.exit('not in DEPS: ' + ', '.join(missing))

    # Cut from the end so earlier offsets stay valid; take the comma after the
    # value and the rest of a line that is left blank.
    for name, (start, end, _) in sorted(found.items(), key=lambda i: -i[1][0]):
        while text[end] in ' \t':
            end += 1
        if text[end] == ',':
            end += 1
        line_start = text.rfind('\n', 0, start) + 1
        if not text[line_start:start].strip():
            start = line_start
            nl = text.find('\n', end)
            if nl != -1 and not text[end:nl].strip():
                end = nl + 1
        text = text[:start] + text[end:]

    # The result must still parse and have exactly the listed entries gone.
    after = next(n.value for n in ast.parse(text).body
                 if isinstance(n, ast.Assign) and len(n.targets) == 1
                 and getattr(n.targets[0], 'id', None) == 'deps')
    left = {k.value for k in after.keys if isinstance(k, ast.Constant)}
    before = {k.value for k in deps.keys if isinstance(k, ast.Constant)}
    if left != before - set(skip):
        sys.exit('DEPS edit went wrong')
    open(deps_path, 'w').write(text)
    kinds = {}
    for _, _, kind in found.values():
        kinds[kind] = kinds.get(kind, 0) + 1
    print(f'{deps_path}: removed {len(found)} entries ('
          + ', '.join(f'{n} {k}' for k, n in sorted(kinds.items())) + ')')


if __name__ == '__main__':
    main()
