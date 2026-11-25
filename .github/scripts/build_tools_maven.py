#!/usr/bin/env python3
"""Replace prebuilt Android build tools from CIPD with released versions from
Maven (accepted on fdroiddata#3911 instead of building them from source).

Used by gms_variant.py:  tools=r8,turbine,aapt2,protoc
                    or   tools=r8:9.6.1,turbine:1.17.0

  r8       third_party/r8/cipd/lib/r8.jar <- com.android.tools:r8 on Google
           Maven. Chromium rolls R8 to the tip of R8's newest release branch,
           so the same version is used if it is published, else the newest of
           the same major.minor, else the newest one. custom_d8.jar and
           custom_r8.jar (prebuilt jars checked into Chromium) are rebuilt from
           their Java sources against that r8.jar, after changing the two
           uses of R8-internal classes to R8's public API, and the GraalVM native-image
           cipd/bin/custom_d8 is no longer used (dex.py runs the jar instead).
  turbine  third_party/turbine/cipd/turbine.jar <- com.google.turbine:turbine
           (the all-deps jar) on Maven Central, newest release unless a
           version is given. The GraalVM native-image cipd/turbine is no longer
           used.

  aapt2    third_party/android_build_tools/aapt2/cipd/aapt2 <- the binary
           inside com.android.tools.build:aapt2:<version>:linux on Google
           Maven, at the version DEPS pins (aapt2_version).
  protoc   third_party/android_build_tools/protoc/cipd/protoc <-
           com.google.protobuf:protoc:4.<version>:linux-x86_64 on Maven
           Central, at the version DEPS pins (v35.1 -> 4.35.1).

  kotlinc  The jars in third_party/kotlinc/current/lib <- the same artifacts
           on Maven Central, at the version in each jar's manifest (the
           compiler's own version from build.txt). compile_kt.py runs the
           compiler's main class on the JVM instead of the GraalVM
           native-image kotlinc-graalvm, and kotlin-preloader.jar (not on
           Maven, only used by bin/kotlinc) is no longer a build input.

Every download is printed with its sha256, next to the file it replaces.
"""

import hashlib
import json
import io
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


def overwrite(path, data, mode=0o644):
    # CIPD installs its files read-only (and may hard-link them from its cache).
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    os.chmod(d, 0o755)
    if os.path.lexists(path):
        os.chmod(path, 0o644)
        os.unlink(path)
    with open(path, 'wb') as f:
        f.write(data)
    os.chmod(path, mode)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def deps_text(src):
    # DEPS as Chromium has it: fdroid/skip_deps.py cut entries out of src/DEPS.
    r = subprocess.run(['git', '-C', src, 'show', 'HEAD:DEPS'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else open(os.path.join(src, 'DEPS')).read()


def cipd_pins():
    """reports/<version>/cipd-pins.json (record_cipd.py), for packages prebuild
    did not sync (fdroid/replaced-deps.txt): $FDROID_CIPD_PINS."""
    path = os.environ.get('FDROID_CIPD_PINS')
    return json.load(open(path)) if path else {}


def swap_binary(name, path, data, source):
    old = open(path, 'rb').read() if os.path.exists(path) else b''
    same = 'identical to' if old == data else 'replaces'
    print(f'{name}: {source}, {len(data)} bytes, sha256 {sha(data)}; '
          f'{same} the CIPD file (sha256 {sha(old)[:16]})', file=sys.stderr)
    overwrite(path, data, 0o755)


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


EXPAND_FLAG_FILES = """
    // F-Droid build: R8's internal FlagFile is not visible in the released jar.
    // dex.py and proguard.py write one argument per line.
    private static String[] expandFlagFiles(String[] args) throws IOException {
        List<String> out = new ArrayList<>();
        for (String arg : args) {
            if (!arg.startsWith("@")) {
                out.add(arg);
                continue;
            }
            for (String line :
                    java.nio.file.Files.readAllLines(java.nio.file.Paths.get(arg.substring(1)))) {
                if (!line.isEmpty()) {
                    out.add(line);
                }
            }
        }
        return out.toArray(new String[0]);
    }
}
"""


def public_api_only(java):
    """CustomD8/CustomR8 use two classes from R8's internal utils package.
    Google's own r8.jar keeps their names; the released jar on Maven is
    minified, so only R8's public API can be used: ProgramResource.fromBytes
    (same arguments as OneShotByteResource.create) and a local flag-file
    reader."""
    s = open(java).read()
    s = re.sub(r'^import com\.android\.tools\.r8\.utils\.(FlagFile|OneShotByteResource);\n', '', s, flags=re.M)
    s = s.replace('OneShotByteResource.create(', 'ProgramResource.fromBytes(')
    if 'FlagFile.expandFlagFiles(args, null)' in s:
        s = s.replace('FlagFile.expandFlagFiles(args, null)', 'expandFlagFiles(args)')
        end = s.rstrip().rfind('}')
        s = s[:end].rstrip() + '\n' + EXPAND_FLAG_FILES
    left = re.findall(r'com\.android\.tools\.r8\.utils\.\w+|FlagFile\.|OneShotByteResource', s)
    if left:
        sys.exit(f'{java}: still uses R8 internals: {sorted(set(left))}')
    with open(java, 'w') as f:
        f.write(s)


def swap_r8(src, version=None):
    jdk = os.path.join(src, 'third_party/jdk/current/bin')
    r8 = os.path.join(src, 'third_party/r8/cipd/lib/r8.jar')
    if os.path.exists(r8):
        out = subprocess.run([os.path.join(jdk, 'java'), '-cp', r8, 'com.android.tools.r8.R8', '--version'],
                             capture_output=True, text=True).stdout.strip()
        current = (re.search(r'R8 (\S+)', out) or [None, None])[1]
        print(f'r8: Chromium ships {out.splitlines()[0] if out else "?"} '
              f'(sha256 {hashlib.sha256(open(r8, "rb").read()).hexdigest()[:16]})', file=sys.stderr)
    else:
        current = cipd_pins().get('r8_version')
        print(f'r8: not synced; Chromium ships R8 {current} (cipd-pins.json)', file=sys.stderr)
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
        public_api_only(java)
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
    global_synthetics(src, jdk, r8)


def global_synthetics(src, jdk, r8):
    """third_party/r8/cipd/lib/global_synthetics.dex.jar, the way
    third_party/r8/3pp/3pp.py builds it, from the r8.jar now in place."""
    out = os.path.join(src, 'third_party/r8/cipd/lib/global_synthetics.dex.jar')
    min_api = re.search(r"^_MIN_SUPPORTED_SDK_VERSION = '(\d+)'",
                        open(os.path.join(src, 'third_party/r8/3pp/3pp.py')).read(), re.M)[1]
    tmp = tempfile.mkdtemp()
    java = os.path.join(jdk, 'java')
    globals_path = os.path.join(tmp, 'desugar.globals')
    dex_dir = os.path.join(tmp, 'dex')
    os.makedirs(dex_dir)
    subprocess.run([java, '-cp', r8, 'com.android.tools.r8.GlobalSyntheticsGenerator',
                    '--min-api', min_api, '--output', globals_path], check=True)
    subprocess.run([java, '-cp', r8, 'com.android.tools.r8.D8', '--no-desugaring', '--min-api', min_api,
                    '--globals', globals_path, '--output', dex_dir], check=True)
    if sorted(os.listdir(dex_dir)) != ['classes.dex']:
        sys.exit(f'r8: expected a single classes.dex, got {os.listdir(dex_dir)}')
    remove(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w') as z:
        z.write(os.path.join(dex_dir, 'classes.dex'), 'classes.dex')
    shutil.rmtree(tmp)
    print(f'r8: built global_synthetics.dex.jar (min-api {min_api}), sha256 '
          f'{sha(open(out, "rb").read())[:16]}', file=sys.stderr)


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


def swap_aapt2(src, version=None):
    if not version:
        m = re.search(r"'aapt2_version':\s*'version:\d+@([^']+)'", deps_text(src))
        if not m:
            sys.exit('aapt2: aapt2_version not found in DEPS')
        version = m[1]
    jar = fetch(f'{GOOGLE}/com/android/tools/build/aapt2/{version}/aapt2-{version}-linux.jar')
    data = zipfile.ZipFile(io.BytesIO(jar)).read('aapt2')
    swap_binary('aapt2', os.path.join(src, 'third_party/android_build_tools/aapt2/cipd/aapt2'), data,
                f'com.android.tools.build:aapt2:{version}:linux from Google Maven')


def swap_protoc(src, version=None):
    if not version:
        m = re.search(r"android_build_tools/protoc/cipd'.*?'version':\s*'version:\d+@v([0-9.]+)'",
                      deps_text(src), re.S)
        if not m:
            sys.exit('protoc: version not found in DEPS')
        version = '4.' + m[1]
    data = fetch(f'{CENTRAL}/com/google/protobuf/protoc/{version}/protoc-{version}-linux-x86_64.exe')
    swap_binary('protoc', os.path.join(src, 'third_party/android_build_tools/protoc/cipd/protoc'), data,
                f'com.google.protobuf:protoc:{version}:linux-x86_64 from Maven Central')


# lib/<jar> -> (group, artifact); None as version means the jar manifest's.
KOTLINC_JARS = {
    'kotlin-compiler.jar': ('org.jetbrains.kotlin', 'kotlin-compiler'),
    'kotlin-stdlib.jar': ('org.jetbrains.kotlin', 'kotlin-stdlib'),
    'kotlin-reflect.jar': ('org.jetbrains.kotlin', 'kotlin-reflect'),
    'kotlin-script-runtime.jar': ('org.jetbrains.kotlin', 'kotlin-script-runtime'),
    'kotlin-scripting-common.jar': ('org.jetbrains.kotlin', 'kotlin-scripting-common'),
    'kotlin-scripting-jvm.jar': ('org.jetbrains.kotlin', 'kotlin-scripting-jvm'),
    'kotlin-scripting-compiler.jar': ('org.jetbrains.kotlin', 'kotlin-scripting-compiler'),
    'kotlin-scripting-compiler-impl.jar': ('org.jetbrains.kotlin', 'kotlin-scripting-compiler-impl'),
    'jvm-abi-gen.jar': ('org.jetbrains.kotlin', 'jvm-abi-gen'),
    'compose-compiler-plugin.jar': ('org.jetbrains.kotlin', 'kotlin-compose-compiler-plugin'),
    'annotations-13.0.jar': ('org.jetbrains', 'annotations'),
    'kotlinx-coroutines-core-jvm.jar': ('org.jetbrains.kotlinx', 'kotlinx-coroutines-core-jvm'),
}
# Classpath for running the compiler without bin/kotlinc and its preloader.
KOTLINC_CLASSPATH = ['kotlin-compiler.jar', 'kotlin-stdlib.jar', 'kotlin-reflect.jar',
                     'kotlin-script-runtime.jar', 'kotlinx-coroutines-core-jvm.jar',
                     'annotations-13.0.jar']


def jar_version(path):
    try:
        man = zipfile.ZipFile(path).read('META-INF/MANIFEST.MF').decode(errors='replace')
    except (KeyError, zipfile.BadZipFile):
        return None
    m = re.search(r'^Implementation-Version:\s*(\S+)', man, re.M)
    return m[1] if m else None


def swap_kotlinc(src, version=None):
    home = os.path.join(src, 'third_party/kotlinc/current')
    lib = os.path.join(home, 'lib')
    bt = os.path.join(home, 'build.txt')
    synced = os.path.isdir(lib)
    if synced:
        build_txt = (open(bt).read().strip() if os.path.exists(bt)
                     else jar_version(os.path.join(lib, 'kotlin-compiler.jar')) or '')
    else:
        # Not synced (fdroid/replaced-deps.txt): fetch every jar.
        build_txt = cipd_pins().get('kotlinc_build') or ''
    m = re.match(r'(\d+\.\d+\.\d+)', build_txt)
    if not (version or m):
        sys.exit(f'kotlinc: cannot tell the compiler version ({build_txt!r}); use tools=kotlinc:<version>')
    kv = version or m[1]
    print(f'kotlinc: Chromium ships {build_txt}; compiler {kv}', file=sys.stderr)
    pom = fetch(f'{CENTRAL}/org/jetbrains/kotlin/kotlin-compiler/{kv}/kotlin-compiler-{kv}.pom').decode()
    pom_versions = dict(re.findall(r'<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>', pom))
    same = diff = 0
    for name, (g, a) in KOTLINC_JARS.items():
        path = os.path.join(lib, name)
        if synced and not os.path.exists(path):
            print(f'kotlinc: {name} not in this kotlinc', file=sys.stderr)
            continue
        if name == 'annotations-13.0.jar':
            v = '13.0'
        elif g == 'org.jetbrains.kotlin' and a not in ('kotlin-reflect', 'kotlin-stdlib'):
            v = kv
        else:
            v = (os.path.exists(path) and jar_version(path)) or pom_versions.get(a) or kv
            v = re.match(r'[0-9][0-9A-Za-z.\-]*', v)[0]
        data = fetch(f"{CENTRAL}/{g.replace('.', '/')}/{a}/{v}/{a}-{v}.jar")
        old = open(path, 'rb').read() if os.path.exists(path) else b''
        same += old == data
        diff += old != data
        print(f'kotlinc: {name} <- {g}:{a}:{v} from Maven Central, sha256 {sha(data)}; '
              f'{"identical to" if old == data else "replaces"} the CIPD file ({sha(old)[:16]})',
              file=sys.stderr)
        overwrite(path, data)
    print(f'kotlinc: {same} jars identical to Chromium\'s, {diff} replaced', file=sys.stderr)
    if not synced:
        with open(bt, 'w') as f:
            f.write(build_txt + '\n')
        # bin/kotlinc is a build input (config.gni) though compile_kt.py runs
        # the compiler on the JVM (below): a script that does the same.
        kotlinc = os.path.join(home, 'bin', 'kotlinc')
        os.makedirs(os.path.dirname(kotlinc), exist_ok=True)
        with open(kotlinc, 'w') as f:
            f.write('#!/bin/sh\n# F-Droid build: the Kotlin compiler from the Maven Central jars in ../lib.\n'
                    'lib=$(dirname "$0")/../lib\n'
                    'exec java -cp "' + ':'.join(f'$lib/{j}' for j in KOTLINC_CLASSPATH) + '" '
                    'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler -kotlin-home "$lib/.." "$@"\n')
        os.chmod(kotlinc, 0o755)

    # Run the compiler on the JVM (the else branch compile_kt.py uses on
    # other hosts runs bin/kotlinc, which needs kotlin-preloader.jar).
    cp = ', '.join(f"os.path.join(build_utils.KOTLIN_HOME, 'lib', '{j}')" for j in KOTLINC_CLASSPATH)
    sub_once(os.path.join(src, 'build/android/gyp/compile_kt.py'),
             r"    if sys\.platform == 'linux' and platform\.machine\(\) == 'x86_64':\n",
             "    if False:  # F-Droid build: no GraalVM native-image kotlinc\n")
    sub_once(os.path.join(src, 'build/android/gyp/compile_kt.py'),
             r"        kotlinc_cmd = \[\n            build_utils\.KOTLINC_PATH,\n.*?'-J-Xmx1G',\n        \]\n",
             "        kotlinc_cmd = [\n"
             "            build_utils.JAVA_PATH,\n"
             "            '-Xmx1G',\n"
             f"            '-cp', ':'.join([{cp}]),\n"
             "            'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',\n"
             "            '-kotlin-home',\n"
             "            build_utils.KOTLIN_HOME,\n"
             "            '-Xdisable-default-scripting-plugin',\n"
             "        ]\n", flags=re.M | re.S)
    gni = os.path.join(src, 'build/config/android/config.gni')
    for rel in ('bin/kotlinc-graalvm', 'lib/kotlin-preloader.jar'):
        sub_once(gni, r'^\s*"//third_party/kotlinc/current/' + re.escape(rel) + r'",\n', '')
        remove(os.path.join(home, rel))
    print('kotlinc: compile_kt.py runs K2JVMCompiler on the JVM; removed kotlinc-graalvm '
          'and kotlin-preloader.jar', file=sys.stderr)


def apply(src, value):
    for item in value.split(','):
        name, _, version = item.partition(':')
        if name == 'r8':
            swap_r8(src, version or None)
        elif name == 'turbine':
            swap_turbine(src, version or None)
        elif name == 'aapt2':
            swap_aapt2(src, version or None)
        elif name == 'protoc':
            swap_protoc(src, version or None)
        elif name == 'kotlinc':
            swap_kotlinc(src, version or None)
        else:
            sys.exit(f'unknown tool {name!r} (r8, turbine, aapt2, protoc, kotlinc)')


if __name__ == '__main__':
    apply(sys.argv[1], sys.argv[2])
