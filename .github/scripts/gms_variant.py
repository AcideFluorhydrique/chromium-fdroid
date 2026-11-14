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

  stubs          Build fdroid/stubs (Play Core, Firebase and InstanceID API
                 surface implemented as "not available") as //fdroid_stubs and
                 use it for those targets instead of empty groups.
  genstubs       Also generate stubs (fdroid/gen_stubs.py) from Google's own
                 jars for the APIs microG does not publish (Cast,
                 identity credentials), only the classes Chromium's Java uses,
                 into //fdroid_stubs. microG's Cast libraries are left out.
  androidx=release
                 Replace every androidx -SNAPSHOT library (from androidx.dev
                 CI builds, not on Google Maven) with its newest release on
                 Google Maven, pre-release if there is no stable one, by
                 overwriting the CIPD file in place.
  gnargs         Print GN args that switch off ML Kit (use_mlkit_for_aicore)
                 and ARCore/VR/OpenXR/Cardboard.
  patch=NAMES    Small source edits: cast (CastOptions without the Builder
                 microG lacks), shape (Shape Detection without the Vision API),
                 castoff (never add the Cast route providers, so the Cast
                 stubs never run), status (no Status.getConnectionResult(),
                 which microG lacks), fido (Fido2ApiCall's private Play
                 services Binder calls fail instead of using GmsClient).

google_play_services_package is not a GN build argument (it is set with
if (!defined(...)) in //build/config/android/config.gni), so gms=... edits
that file, as Cromite does. Nothing is printed for args.gn any more.
An empty java_group keeps GN happy, so javac then reports every place in
Chromium that still uses the removed library.
"""

import io
import shutil
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

MAVEN = 'https://repo1.maven.org/maven2'
STUB_TARGETS = {
    'google_play_services_iid_java',
    'google_firebase_firebase_common_java',
    'google_firebase_firebase_installations_java',
    'google_firebase_firebase_messaging_java',
}
STUBS_LABEL = '//fdroid_stubs:fdroid_stubs_java'
GEN_STUB_TARGETS = {
    'google_play_services_cast_java': 'play-services-cast',
    'google_play_services_cast_framework_java': 'play-services-cast-framework',
    'google_play_services_identity_credentials_java': 'play-services-identity-credentials',
}
GEN_ARTIFACTS = [
    'com.google.android.gms:play-services-cast:22.2.0',
    'com.google.android.gms:play-services-cast-framework:22.2.0',
    'com.google.android.gms:play-services-identity-credentials:16.0.0-alpha12',
    # Only what microG lacks and Chromium uses is generated (TaskApiCall, GmsClient, ...).
    'com.google.android.gms:play-services-base:18.11.1',
    'com.google.android.gms:play-services-basement:18.12.0',
]
# Compile-time classpath for the generated stubs (Maven, the versions are not critical).
GEN_CLASSPATH = [
    ('https://repo1.maven.org/maven2', 'org/jetbrains/kotlin/kotlin-stdlib/2.1.20/kotlin-stdlib-2.1.20', '.jar'),
    ('https://dl.google.com/dl/android/maven2', 'androidx/mediarouter/mediarouter/1.7.0/mediarouter-1.7.0', '.aar'),
    ('https://dl.google.com/dl/android/maven2', 'androidx/core/core/1.13.1/core-1.13.1', '.aar'),
    ('https://dl.google.com/dl/android/maven2', 'androidx/fragment/fragment/1.8.5/fragment-1.8.5', '.aar'),
    ('https://dl.google.com/dl/android/maven2', 'androidx/appcompat/appcompat/1.7.0/appcompat-1.7.0', '.aar'),
    ('https://dl.google.com/dl/android/maven2', 'androidx/annotation/annotation-jvm/1.9.1/annotation-jvm-1.9.1', '.jar'),
]
# GN targets the generated stubs depend on, if they exist in this checkout.
GEN_DEPS = [
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_mediarouter_mediarouter_java'),
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_core_core_java'),
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_fragment_fragment_java'),
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_appcompat_appcompat_java'),
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_annotation_annotation_java'),
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_annotation_annotation_jvm_java'),
    # play-services-identity-credentials brings androidx.credentials along.
    ('third_party/androidx/BUILD.gn', '//third_party/androidx', 'androidx_credentials_credentials_java'),
]
GN_ARGS = [
    'use_mlkit_for_aicore = false',
    'enable_arcore = false',
    'enable_vr = false',
    'enable_openxr = false',
    'enable_cardboard = false',
]
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


def gen_stubs(src, microg_jar, out_dir):
    import subprocess
    import tempfile
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = tempfile.mkdtemp()
    sdk = os.path.join(src, 'third_party/android_sdk/public/platforms')
    android_jar = sorted(os.path.join(sdk, d, 'android.jar') for d in os.listdir(sdk)
                         if os.path.exists(os.path.join(sdk, d, 'android.jar')))[-1]
    cp = [android_jar, microg_jar]
    for repo, path, ext in GEN_CLASSPATH:
        data = fetch(f'{repo}/{path}{ext}')
        jar = os.path.join(tmp, os.path.basename(path) + '.jar')
        with open(jar, 'wb') as f:
            f.write(zipfile.ZipFile(io.BytesIO(data)).read('classes.jar') if ext == '.aar' else data)
        cp.append(jar)
    files = subprocess.run(['git', '-C', src, 'grep', '-l', 'com.google.android.gms', '--', '*.java'],
                           capture_output=True, text=True).stdout.split()
    roots = set()
    # Formatted code splits long qualified names over lines, so allow whitespace around dots.
    name = re.compile(r'com\s*\.\s*google\s*\.\s*android\s*\.\s*gms(?:\s*\.\s*[A-Za-z0-9_]+)+')
    for f in files:
        with open(os.path.join(src, f), errors='ignore') as fh:
            roots |= {re.sub(r'\s+', '', m) for m in name.findall(fh.read())}
    roots_file = os.path.join(tmp, 'roots.txt')
    with open(roots_file, 'w') as f:
        f.write('\n'.join(sorted(roots)))
    print(f'genstubs: {len(roots)} com.google.android.gms names in {len(files)} Java files', file=sys.stderr)
    cmd = [sys.executable, os.path.join(here, '..', '..', 'fdroid', 'gen_stubs.py'), '--out', out_dir,
           '--exclude-jar', microg_jar, '--classpath', ':'.join(cp), '--roots', roots_file]
    for a in GEN_ARTIFACTS:
        cmd += ['--artifact', a]
    subprocess.run(cmd, check=True, stdout=sys.stderr)


def gen_deps(src):
    # Defined outside android_deps/BUILD.gn, but every androidx target depends on it.
    out = ['//third_party/android_deps:kotlin_stdlib_java']
    for path, label, name in GEN_DEPS:
        p = os.path.join(src, path)
        if os.path.exists(p) and re.search(rf'\("{name}"\)', open(p).read()):
            out.append(f'{label}:{name}')
    return out


def write_stubs(src, generated=False):
    here = os.path.dirname(os.path.abspath(__file__))
    stubs = os.path.join(here, '..', '..', 'fdroid', 'stubs', 'java')
    dst = os.path.join(src, 'fdroid_stubs')
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(stubs, os.path.join(dst, 'java'))
    deps = ['$google_play_services_package:google_play_services_tasks_java']
    if generated:
        gen_stubs(src, os.path.join(src, 'fdroid_gms', 'microg.jar'), os.path.join(dst, 'java', 'src'))
        deps += ['$google_play_services_package:google_play_services_base_java',
                 '$google_play_services_package:google_play_services_basement_java'] + gen_deps(src)
    sources = sorted(
        os.path.relpath(os.path.join(r, f), dst)
        for r, _, fs in os.walk(os.path.join(dst, 'java')) for f in fs if f.endswith('.java'))
    with open(os.path.join(dst, 'BUILD.gn'), 'w') as f:
        f.write('import("//build/config/android/config.gni")\n')
        f.write('import("//build/config/android/rules.gni")\n\n')
        f.write('android_library("fdroid_stubs_java") {\n')
        f.write('  chromium_code = false\n')
        f.write('  sources = [\n')
        f.writelines(f'    "{x}",\n' for x in sources)
        f.write('  ]\n')
        f.write('  deps = [\n')
        f.writelines(f'    "{x}",\n' for x in deps)
        f.write('  ]\n')
        f.write('}\n')
    print(f'fdroid_stubs: {len(sources)} classes', file=sys.stderr)


def patch_file(path, old, new, count=1):
    s = open(path).read()
    if s.count(old) != count:
        sys.exit(f'{path}: expected {count} occurrence(s) of {old!r}')
    with open(path, 'w') as f:
        f.write(s.replace(old, new))


def block_end(s, start):
    """Index just past the brace block that starts at the first '{' after start."""
    i = s.index('{', start)
    depth = 0
    while True:
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1


def patch_fido(path):
    """Fido2ApiCall talks to Play services' private FIDO2 Binder service through
    Google's internal GmsClient/TaskApiCall API, which microG's GoogleApi and
    Api.Client do not match. Keep its constants and result classes, make every
    call fail (callers already handle a failed Task), and reduce FidoClient to a
    placeholder type for the static Api objects."""
    s = open(path).read()
    head = '    private static final class FidoClient extends GmsClient<Interface> {'
    if s.count(head) != 1:
        sys.exit(f'{path}: FidoClient not found')
    i = s.index(head)
    s = s[:i] + (
        '    private abstract static class FidoClient implements Api.Client {\n'
        '        public static class Builder\n'
        '                extends Api.AbstractClientBuilder<FidoClient, ApiOptions.NoOptions> {\n'
        '            Builder(String descriptor, String startServiceAction, int apiId) {}\n'
        '        }\n'
        '    }') + s[block_end(s, i):]
    run = s.index('        return doRead(\n')
    end = s.index('.build());\n', run) + len('.build());\n')
    s = s[:run] + ('        args.recycle();\n'
                   '        return com.google.android.gms.tasks.Tasks.forException(\n'
                   '                new UnsupportedOperationException("FIDO2 API not available in this build"));\n') + s[end:]
    s = s.replace('        super(context, apiParams.mApi, ApiOptions.NO_OPTIONS, new ApiExceptionMapper());',
                  '        super(context, apiParams.mApi, ApiOptions.NO_OPTIONS);')
    with open(path, 'w') as f:
        f.write(s)
    print('patched Fido2ApiCall: calls fail, no GmsClient', file=sys.stderr)


def apply_patches(src, names):
    if 'cast' in names:
        path = os.path.join(src, 'components/media_router/browser/android/java/src/org/chromium/components/media_router/caf/CastOptionsProvider.java')
        s = open(path).read()
        new = re.sub(r'return new CastOptions\.Builder\(\).*?\.build\(\);', 'return new CastOptions();', s, count=1, flags=re.S)
        if new == s:
            sys.exit(f'{path}: CastOptions.Builder chain not found')
        with open(path, 'w') as f:
            f.write(new)
        print('patched CastOptionsProvider: new CastOptions()', file=sys.stderr)
    if 'shape' in names:
        d = os.path.join(src, 'services/shape_detection')
        gn = os.path.join(d, 'BUILD.gn')
        for line in ('      "android/java/src/org/chromium/shape_detection/FaceDetectionImplGmsCore.java",\n',
                     '      "android/java/src/org/chromium/shape_detection/TextDetectionImpl.java",\n',
                     '      "$google_play_services_package:google_play_services_vision_common_java",\n',
                     '      "$google_play_services_package:google_play_services_vision_java",\n'):
            patch_file(gn, line, '')
        j = os.path.join(d, 'android/java/src/org/chromium/shape_detection')
        patch_file(os.path.join(j, 'FaceDetectionProviderImpl.java'),
                   'FaceDetection.MANAGER.bind(new FaceDetectionImplGmsCore(options), request);',
                   'FaceDetection.MANAGER.bind(new FaceDetectionImpl(options), request);')
        patch_file(os.path.join(j, 'InterfaceRegistrar.java'),
                   'TextDetection impl = TextDetectionImpl.create();',
                   'TextDetection impl = null;')
        print('patched shape_detection: no Vision API', file=sys.stderr)
    if 'castoff' in names:
        path = os.path.join(src, 'components/media_router/browser/android/java/src/org/chromium/components/media_router/BrowserMediaRouter.java')
        patch_file(path, 'public void addProviders(MediaRouteManager manager) {\n',
                   'public void addProviders(MediaRouteManager manager) {\n'
                   '                    if (true) return; // F-Droid build: no Cast.\n')
        print('patched BrowserMediaRouter: no Cast route providers', file=sys.stderr)
    if 'status' in names:
        path = os.path.join(src, 'chrome/browser/password_manager/android/java/src/org/chromium/chrome/browser/password_manager/PasswordManagerAndroidBackendUtil.java')
        patch_file(path, '((ApiException) exception).getStatus().getConnectionResult();', 'null;')
        print('patched PasswordManagerAndroidBackendUtil: no getConnectionResult()', file=sys.stderr)
    if 'fido' in names:
        patch_fido(os.path.join(src, 'components/webauthn/android/java/src/org/chromium/components/webauthn/Fido2ApiCall.java'))


def androidx_releases(src):
    import json
    google = 'https://dl.google.com/dl/android/maven2'
    bom = json.load(open(os.path.join(src, 'third_party/androidx/bill_of_materials.json')))
    done, missing = [], []
    for e in bom:
        g, n, v = e['group'], e['name'], e['version']
        if not v.endswith('-SNAPSHOT'):
            continue
        d = os.path.join(src, 'third_party/androidx/cipd/libs', re.sub(r'[.\-]', '_', f'{g}_{n}'))
        if not os.path.isdir(d):
            continue
        try:
            meta = fetch(f"{google}/{g.replace('.', '/')}/{n}/maven-metadata.xml").decode()
        except Exception:
            missing.append(f'{g}:{n}')
            continue
        vs = re.findall(r'<version>([^<]+)</version>', meta)
        stable = [x for x in vs if re.fullmatch(r'[0-9.]+', x)]
        rel = (stable or vs)[-1]
        for f in os.listdir(d):
            ext = os.path.splitext(f)[1]
            if ext not in ('.aar', '.jar'):
                continue
            try:
                data = fetch(f"{google}/{g.replace('.', '/')}/{n}/{rel}/{n}-{rel}{ext}")
            except urllib.error.HTTPError:
                missing.append(f'{g}:{n}:{rel}{ext}')
                continue
            with open(os.path.join(d, f), 'wb') as out:
                out.write(data)
        done.append(f'{g}:{n} {v} -> {rel}')
    print(f'androidx: {len(done)} snapshots replaced with releases, {len(missing)} not on Google Maven',
          file=sys.stderr)
    for x in done + [f'{m} (kept the snapshot)' for m in missing]:
        print('  ' + x, file=sys.stderr)


def write_gms_dir(src, mode, stubs=False, genstubs=False):
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
            if genstubs and n in GEN_STUB_TARGETS:
                continue
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
        elif stubs and (n in STUB_TARGETS or (genstubs and n in GEN_STUB_TARGETS)):
            lines += [f'java_group("{n}") {{', f'  deps = [ "{STUBS_LABEL}" ]', '}', '']
        else:
            lines += [f'java_group("{n}") {{', '  deps = []', '}', '']
    with open(os.path.join(d, 'BUILD.gn'), 'w') as f:
        f.write('\n'.join(lines))
    print(f'fdroid_gms: {len(wanted)} targets from microG, '
          f'{len(names) - len(wanted)} empty', file=sys.stderr)
    for p in provided:
        print('  ' + p, file=sys.stderr)


def drop_android_deps(src, groups, stubs=False):
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
        dep = f'"{STUBS_LABEL}"' if stubs and DROP_GROUPS['playcore'].search(name) else ''
        out.append(f'java_group("{name}") {{\n    deps = [ {dep} ]\n  }}')
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
    stubs = 'stubs' in spec or 'genstubs' in spec
    genstubs = 'genstubs' in spec
    if genstubs and 'gms=microg' not in spec:
        sys.exit('genstubs needs gms=microg (it compiles against the microG jar)')
    for item in spec:
        key, _, value = item.partition('=')
        if key == 'gms':
            assert value in ('microg', 'drop'), item
            write_gms_dir(src, value, stubs, genstubs)
            set_gms_package(src)
        elif key == 'drop':
            groups = value.split(',')
            assert all(g in DROP_GROUPS for g in groups), item
            drop_android_deps(src, groups, stubs)
            if 'impress' in groups:
                drop_xr_module(src)
        elif key in ('stubs', 'genstubs'):
            pass
        elif key == 'androidx':
            assert value == 'release', item
            androidx_releases(src)
        elif key == 'gnargs':
            args += GN_ARGS
        elif key == 'patch':
            apply_patches(src, value.split(','))
        else:
            sys.exit(f'unknown spec item {item}')
    if stubs:
        write_stubs(src, genstubs)
    print('\n'.join(args))


if __name__ == '__main__':
    main()
