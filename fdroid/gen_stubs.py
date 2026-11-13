#!/usr/bin/env python3
"""Generate compile-only Java stubs from the public API of Maven artifacts.

Usage:
  gen_stubs.py --out DIR [--exclude-jar JAR ...] [--classpath JAR:JAR...]
               [--roots FILE] --artifact group:name:version[:Class,Class...] ...

For each artifact (Google Maven, then Maven Central), the public classes are
read with javap and written as Java sources with the same signatures and empty
bodies (methods return null/0/false). With a class list after the version,
only those classes (and their nested classes) are generated. Classes that the
--exclude-jar jars already provide (e.g. microG's libraries) are skipped.

The stubs only let Chromium's Java compile without the non-free libraries;
the code paths that would call them are switched off separately, and every
method throws UnsupportedOperationException (Chromium already catches Exception
around most of these calls). Members whose types cannot be resolved are left out.

--roots is a file of class names (e.g. everything matching com.google.android.gms.*
in Chromium's Java): only those classes and the classes their kept signatures
need are generated. --classpath lists the jars the stubs compile against
(android.jar, androidx, Kotlin); with it, only classes they really contain count
as resolvable, and constructors call a superclass constructor that exists.
Obfuscated classes (zza, zzbt, ...) are never generated.
"""

import argparse
import collections
import io
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

REPOS = ['https://dl.google.com/dl/android/maven2', 'https://repo1.maven.org/maven2']
PLATFORM_PREFIXES = ('java.', 'javax.', 'android.', 'androidx.', 'kotlin.', 'org.json.',
                     'dalvik.', 'org.w3c.', 'org.xml.')
PRIMITIVES = {'void', 'boolean', 'byte', 'char', 'short', 'int', 'long', 'float', 'double'}
DEFAULTS = {'boolean': 'false', 'char': "'\\0'", 'void': None}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'gen-stubs/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def download(coord):
    g, a, v = coord
    path = f"{g.replace('.', '/')}/{a}/{v}/{a}-{v}"
    for repo in REPOS:
        for ext in ('.aar', '.jar'):
            try:
                data = fetch(f'{repo}/{path}{ext}')
            except urllib.error.HTTPError:
                continue
            if ext == '.jar':
                return data
            aar = zipfile.ZipFile(io.BytesIO(data))
            return aar.read('classes.jar')
    sys.exit(f'{g}:{a}:{v} not found')


def jar_classes(path_or_bytes):
    z = zipfile.ZipFile(path_or_bytes if isinstance(path_or_bytes, str) else io.BytesIO(path_or_bytes))
    return {n[:-6].replace('/', '.') for n in z.namelist()
            if n.endswith('.class') and not re.search(r'\$\d', n) and 'module-info' not in n}


def split_top(s, sep=','):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '<(':
            depth += 1
        elif ch in '>)':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def dotted(t):
    return t.replace('$', '.')


Member = collections.namedtuple('Member', 'kind mods tparams type name params throws value')
Klass = collections.namedtuple('Klass', 'name mods kind tparams extends implements members')

SKIPPED = []
HEADER = re.compile(
    r'^(?P<mods>(?:(?:public|protected|private|static|final|abstract|sealed|non-sealed)\s+)*)'
    r'(?P<kind>class|interface)\s+(?P<name>[\w.$]+)(?P<tparams><.*?>)?'
    r'(?:\s+extends\s+(?P<ext>.+?))?(?:\s+implements\s+(?P<impl>.+?))?(?:\s+permits\s+.+?)?\s*\{$')


def parse_javap(text):
    classes = []
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('Compiled from') or line.startswith('Picked up'):
            continue
        if cur is None:
            m = HEADER.match(line)
            if m:
                cur = Klass(m['name'], m['mods'].split(), m['kind'], m['tparams'] or '',
                            m['ext'] or '', m['impl'] or '', [])
            continue
        if line == '}':
            classes.append(cur)
            cur = None
            continue
        if not line.endswith(';'):
            continue
        line = line[:-1]
        if line.startswith('static {}'):
            continue
        value = None
        if ' = ' in line and '(' not in line.split(' = ')[0]:
            line, value = line.split(' = ', 1)
        mods = []
        words = line.split(' ')
        while words and words[0] in ('public', 'protected', 'static', 'final', 'abstract', 'default',
                                     'native', 'synchronized', 'transient', 'volatile', 'strictfp'):
            mods.append(words.pop(0))
        rest = ' '.join(words)
        tparams = ''
        if rest.startswith('<'):
            depth = 0
            for i, ch in enumerate(rest):
                depth += ch == '<'
                depth -= ch == '>'
                if depth == 0:
                    tparams, rest = rest[:i + 1], rest[i + 1:].strip()
                    break
        if '(' in rest:
            head, tail = rest.split('(', 1)
            params_s, after = tail.rsplit(')', 1)
            throws = []
            if 'throws' in after:
                throws = [t.strip() for t in after.split('throws', 1)[1].split(',')]
            head_parts = head.rsplit(' ', 1)
            if len(head_parts) == 1:
                rtype, name, kind = None, head_parts[0], 'ctor'
            else:
                rtype, name, kind = head_parts[0], head_parts[1], 'method'
            cur.members.append(Member(kind, mods, tparams, rtype, name,
                                      split_top(params_s), throws, None))
        else:
            parts = rest.rsplit(' ', 1)
            if len(parts) != 2:
                SKIPPED.append(raw.strip())
                continue
            cur.members.append(Member('field', mods, '', parts[0], parts[1], [], [], value))
    return classes


OBFUSCATED = re.compile(r'(^|[.$])zz[a-z]{1,3}($|[.$])')


def erase(t):
    while '<' in t:
        t2 = re.sub(r'<[^<>]*>', '', t)
        if t2 == t:
            break
        t = t2
    return dotted(t).replace('...', '[]').strip()


def type_names(t):
    t = re.sub(r'\b(extends|super)\b', ' ', t)
    return {n for n in re.findall(r'[A-Za-z_][\w.$]*', t) if '.' in n}


class Generator:
    def __init__(self, known, generated, classpath=None, cp_classes=None):
        self.known = known          # classes from the exclude jars
        self.generated = generated  # classes we generate
        self.classpath = classpath
        self.cp_classes = cp_classes
        self.dropped = 0
        self._ctors = {}

    def resolvable(self, t):
        for n in type_names(t):
            if OBFUSCATED.search(n) or n.startswith('kotlin.jvm.internal.'):
                return False
            if n in self.known or n in self.generated:
                continue
            if self.cp_classes is not None:
                if n in self.cp_classes or n.startswith('java.'):
                    continue
            elif n.startswith(PLATFORM_PREFIXES):
                continue
            return False
        return True

    def super_args(self, sup):
        """Arguments for a super(...) call when the superclass has no no-arg constructor."""
        sup = erase(sup)
        if sup in self.generated or not self.classpath or sup == 'java.lang.Object':
            return ''
        if sup not in self._ctors:
            r = subprocess.run(['javap', '-public', '-protected', '-cp', self.classpath, sup],
                               capture_output=True, text=True)
            ctors = [m for k in parse_javap(r.stdout) for m in k.members if m.kind == 'ctor']
            ctors.sort(key=lambda m: len(m.params))
            self._ctors[sup] = ctors[0].params if ctors else []
        return ', '.join(f'({erase(p)}) {self.default_value(erase(p))}' for p in self._ctors[sup])

    def default_value(self, t):
        t = t.strip()
        if t in DEFAULTS:
            return DEFAULTS[t]
        if t in PRIMITIVES:
            return '0'
        return 'null'

    def emit(self, k, nested, indent=''):
        simple = k.name.rsplit('.', 1)[-1].rsplit('$', 1)[-1]
        is_annotation = k.kind == 'interface' and 'java.lang.annotation.Annotation' in k.extends
        is_enum = k.extends.startswith('java.lang.Enum<')
        mods = [m for m in k.mods if m in ('public', 'protected', 'abstract', 'static')]
        if indent and 'static' not in mods and k.kind == 'class':
            mods.append('static')
        if is_enum or is_annotation:
            mods = [m for m in mods if m != 'abstract']
        tparams = re.sub(r'\s+extends\s+java\.lang\.Object\b', '', dotted(k.tparams))
        out = []
        if is_annotation:
            out.append(f'{indent}{" ".join(mods)} @interface {simple} {{')
        elif is_enum:
            out.append(f'{indent}{" ".join(m for m in mods if m != "abstract")} enum {simple} {{')
            consts = [m.name for m in k.members if m.kind == 'field' and dotted(m.type) == dotted(k.name)]
            out.append(f'{indent}  {", ".join(consts)};')
        else:
            head = f'{indent}{" ".join(mods)} {k.kind} {simple}{tparams}'
            if k.extends and k.kind == 'class' and self.resolvable(k.extends) \
                    and dotted(k.extends) != 'java.lang.Object':
                head += f' extends {dotted(k.extends)}'
            sups = [dotted(s) for s in split_top(k.extends if k.kind == 'interface' else k.implements)
                    if s and self.resolvable(s)]
            if sups:
                head += (' extends ' if k.kind == 'interface' else ' implements ') + ', '.join(sups)
            out.append(head + ' {')
        has_noarg = False
        sup_call = ''
        if k.kind == 'class' and not is_enum and k.extends and self.resolvable(k.extends):
            a = self.super_args(k.extends)
            if a:
                sup_call = f' super({a});'
        seen = set()
        members = sorted(k.members, key=lambda m: m.kind != 'field' and m.type == 'java.lang.Object')
        for m in members:
            sig_types = [m.type or ''] + m.params + m.throws
            if not all(self.resolvable(t) for t in sig_types if t):
                self.dropped += 1
                continue
            key = (m.kind, m.name, tuple(erase(p) for p in m.params))
            if m.kind != 'field' and key in seen:
                continue
            seen.add(key)
            mm = [x for x in m.mods if x in ('public', 'protected', 'static', 'abstract', 'default')]
            if m.kind == 'field':
                if is_enum and dotted(m.type) == dotted(k.name):
                    continue
                t = dotted(m.type)
                if is_annotation or k.kind == 'interface':
                    mm = []
                init = m.value
                if init is None and 'final' in m.mods:
                    init = self.default_value(t)
                    if dotted(m.type) in self.generated and dotted(m.type).startswith(dotted(k.name) + '.'):
                        init = f'new {dotted(m.type)}()'
                if 'final' in m.mods and 'static' in m.mods:
                    mm.append('final')
                if init is not None and t == 'java.lang.String' and m.value is not None and not init.startswith('"'):
                    init = '"' + init + '"'
                if t == 'long' and m.value is not None:
                    init = init.rstrip('lL') + 'L'
                if t == 'float' and m.value is not None:
                    init = init.rstrip('fF') + 'f'
                if t == 'double' and m.value is not None:
                    init = init.rstrip('dD')
                if t in ('double', 'float') and m.value is not None:
                    w = 'Double' if t == 'double' else 'Float'
                    init = {'Infinity': f'{w}.POSITIVE_INFINITY', '-Infinity': f'{w}.NEGATIVE_INFINITY',
                            'NaN': f'{w}.NaN'}.get(init.rstrip('fF'), init)
                out.append(f'{indent}  {" ".join(mm)} {t} {m.name}' + (f' = {init};' if init is not None else ';'))
                continue
            params = ', '.join(f'{dotted(p)} p{i}' for i, p in enumerate(m.params))
            throws = f' throws {", ".join(dotted(t) for t in m.throws)}' if m.throws else ''
            tp = re.sub(r'\s+extends\s+java\.lang\.Object\b', '', dotted(m.tparams))
            if m.kind == 'ctor':
                if is_enum or k.kind == 'interface':
                    continue
                has_noarg |= not m.params
                vis = 'public' if 'public' in mm else 'protected'
                out.append(f'{indent}  {vis} {tp + " " if tp else ""}{simple}({params}){throws} {{{sup_call} }}')
                continue
            if is_annotation:
                out.append(f'{indent}  {dotted(m.type)} {m.name}();')
                continue
            body_less = 'abstract' in mm or (k.kind == 'interface' and 'static' not in mm and 'default' not in mm)
            if k.kind == 'interface':
                mm = [x for x in mm if x not in ('public', 'abstract')]
            rt = dotted(m.type)
            if body_less:
                out.append(f'{indent}  {" ".join(mm)} {tp + " " if tp else ""}{rt} {m.name}({params}){throws};')
            else:
                body = '{ throw new UnsupportedOperationException("not available in this build"); }'
                out.append(f'{indent}  {" ".join(mm)} {tp + " " if tp else ""}{rt} {m.name}({params}){throws} {body}')
        if k.kind == 'class' and not is_enum and not is_annotation and not has_noarg:
            out.append(f'{indent}  protected {simple}() {{{sup_call} }}')
        for n in nested.get(k.name, []):
            out += self.emit(n, nested, indent + '  ')
        out.append(f'{indent}}}')
        return out


def reachable(parsed, tokens, known):
    by_dotted = {dotted(n): n for n in parsed}
    todo = []
    for t in tokens:
        t = t.rstrip('.;')
        while t and t not in by_dotted:
            t = t.rsplit('.', 1)[0] if '.' in t else ''
        if t:
            todo.append(by_dotted[t])
    keep = set()
    while todo:
        n = todo.pop()
        if n in keep:
            continue
        keep.add(n)
        k = parsed[n]
        refs = set()
        for t in [k.extends, k.implements, k.tparams]:
            refs |= type_names(t)
        for m in k.members:
            for t in [m.type or '', m.tparams] + m.params + m.throws:
                refs |= type_names(t)
        if '$' in n:
            refs.add(dotted(n.rsplit('$', 1)[0]))
        for r in refs:
            if r in by_dotted and r not in known:
                todo.append(by_dotted[r])
    # Nested classes are emitted inside their outer class, so keep the outers.
    for n in list(keep):
        while '$' in n:
            n = n.rsplit('$', 1)[0]
            if n in parsed:
                keep.add(n)
    print(f'{len(keep)} of {len(parsed)} classes reachable from the roots', file=sys.stderr)
    return {n: parsed[n] for n in keep}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--exclude-jar', action='append', default=[])
    ap.add_argument('--artifact', action='append', required=True)
    ap.add_argument('--classpath')
    ap.add_argument('--roots')
    args = ap.parse_args()

    cp_classes = None
    if args.classpath:
        cp_classes = set()
        for j in args.classpath.split(':'):
            if j:
                cp_classes |= {dotted(n) for n in jar_classes(j)}

    known = set()
    for j in args.exclude_jar:
        known |= jar_classes(j)

    tmp = tempfile.mkdtemp()
    parsed = {}
    for spec in args.artifact:
        parts = spec.split(':')
        coord, only = parts[:3], (parts[3].split(',') if len(parts) > 3 else None)
        data = download(coord)
        jar = os.path.join(tmp, f'{coord[1]}.jar')
        open(jar, 'wb').write(data)
        names = sorted(jar_classes(jar) - known)
        if only:
            names = [n for n in names if any(n == o or n.startswith(o + '$') for o in only)]
        for i in range(0, len(names), 200):
            r = subprocess.run(['javap', '-public', '-constants', '-cp', jar] + names[i:i + 200],
                               capture_output=True, text=True)
            for k in parse_javap(r.stdout):
                if 'public' in k.mods or 'protected' in k.mods:
                    parsed[k.name] = k
        print(f'{":".join(coord)}: {len(names)} classes read', file=sys.stderr)

    parsed = {n: k for n, k in parsed.items() if not OBFUSCATED.search(n)}
    if args.roots:
        parsed = reachable(parsed, open(args.roots).read().split(), known)
    generated = {dotted(n) for n in parsed}
    gen = Generator(known, generated, args.classpath, cp_classes)
    nested = collections.defaultdict(list)
    tops = []
    for name, k in parsed.items():
        if '$' in name and name.rsplit('$', 1)[0] in parsed:
            nested[name.rsplit('$', 1)[0]].append(k)
        elif '$' not in name:
            tops.append(k)
    for k in tops:
        pkg, simple = k.name.rsplit('.', 1)
        path = os.path.join(args.out, *pkg.split('.'), simple + '.java')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = '\n'.join(gen.emit(k, nested))
        with open(path, 'w') as f:
            f.write('// Generated by fdroid/gen_stubs.py: compile-only stub, the bodies never run.\n')
            f.write(f'package {pkg};\n\n{body}\n')
    print(f'generated {len(tops)} files ({len(parsed)} classes), dropped {gen.dropped} members '
          'with unresolvable types', file=sys.stderr)
    if SKIPPED:
        print(f'skipped {len(SKIPPED)} javap lines it could not parse, e.g.:', file=sys.stderr)
        for line in SKIPPED[:10]:
            print('  ' + line, file=sys.stderr)


if __name__ == '__main__':
    main()
