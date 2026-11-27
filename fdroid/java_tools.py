#!/usr/bin/env python3
"""Build the Android build tools Chromium takes from CIPD, the way its 3pp
scripts make them, from source or Maven.

Usage: java_tools.py <chromium src dir> <cipd-pins.json>

prebuild does not sync these packages (fdroid/replaced-deps.txt):

  error_prone, error_prone_javac, nullaway, manifest_merger, signflinger
      build/3pp_common/maven.py: a pom.xml with the one artifact and
      `mvn assembly:single` (jar-with-dependencies), from Maven Central or
      Google Maven, at the version cipd-pins.json read from Chromium's jar.
      nullaway without the com/google classes error_prone has (its 3pp.py),
      signflinger plus Chromium's ZipBuilder.java (its 3pp.py). The GraalVM
      native image of signflinger is not built: zipbuilder.py uses the jar,
      as it does on hosts without the CPU features the image needs.
  bazel_tools/cipd/ijar
      Bazel's third_party/ijar at the version bazel_tools/3pp/3pp.pb names,
      compiled with the system's g++ and zlib (Chromium builds it with Bazel;
      singlejar and zipper, which the build does not use, are left out).
  aosp_dalvik/cipd/lib/dx.jar
      AOSP's platform/dalvik dx at the commit aosp_dalvik/3pp/3pp.pb names,
      compiled with javac --release 11 (its 3pp/install.sh).
  android_system_sdk/cipd/android_system.jar
      Chromium's copy is an internal build of the system API stubs; AOSP
      publishes the same stubs in platform/prebuilts/sdk
      (current/system/android.jar, Apache-2.0), fetched at a pinned commit.
      base:flagged_apis_java compiles against them (WebViewDelegate).
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

CENTRAL = 'https://repo.maven.apache.org/maven2'
GOOGLE = 'https://dl.google.com/android/maven2'
TOOLS = 'third_party/android_build_tools'

POM = """<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>group</groupId>
  <artifactId>artifact</artifactId>
  <version>1</version>
  <dependencies>
    <dependency>
      <groupId>{group}</groupId>
      <artifactId>{artifact}</artifactId>
      <version>{version}</version>
      <scope>runtime</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <artifactId>maven-assembly-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <descriptorRefs>
            <descriptorRef>jar-with-dependencies</descriptorRef>
          </descriptorRefs>
        </configuration>
        <executions>
          <execution>
            <phase>package</phase>
            <goals><goal>single</goal></goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
  <repositories>
    <repository>
      <id>repo</id>
      <url>{repo}</url>
    </repository>
  </repositories>
</project>
"""

# name -> (cipd jar path, repository)
MAVEN_TOOLS = {
    'error_prone': ('error_prone/cipd/error_prone_core.jar', CENTRAL),
    'error_prone_javac': ('error_prone_javac/cipd/javac.jar', CENTRAL),
    'nullaway': ('nullaway/cipd/nullaway.jar', CENTRAL),
    'manifest_merger': ('manifest_merger/cipd/manifest-merger.jar', GOOGLE),
    'signflinger': ('signflinger/cipd/signflinger.jar', GOOGLE),
}


def run(cmd, **kw):
    print('+ ' + ' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def fetch(url):
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def sub_once(path, pattern, repl, flags=re.M):
    s = open(path).read()
    new, n = re.subn(pattern, repl, s, flags=flags)
    if n != 1:
        sys.exit(f'{path}: expected one match of {pattern!r}, found {n}')
    with open(path, 'w') as f:
        f.write(new)


def maven_jar(src, name, tool, work):
    rel, repo = MAVEN_TOOLS[name]
    out = os.path.join(src, TOOLS, rel)
    d = os.path.join(work, name)
    os.makedirs(d)
    with open(os.path.join(d, 'pom.xml'), 'w') as f:
        f.write(POM.format(group=tool['group'], artifact=tool['artifact'],
                           version=tool['version'], repo=repo))
    env = dict(os.environ, JAVA_HOME=os.path.join(src, 'third_party/jdk/current'), MAVEN_SKIP_RC='1')
    run(['mvn', '-B', '-q', 'clean', 'assembly:single', '-f', 'pom.xml'], cwd=d, env=env)
    jar = os.path.join(d, 'target/artifact-1-jar-with-dependencies.jar')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if name == 'nullaway':
        # Its 3pp.py: without the classes errorprone's jar has.
        with zipfile.ZipFile(jar) as zin, zipfile.ZipFile(out, 'w') as zout:
            for info in zin.infolist():
                if not info.is_dir() and not info.filename.startswith('com/google'):
                    zout.writestr(info, zin.read(info))
    else:
        shutil.copyfile(jar, out)
    if name == 'signflinger':
        # Its 3pp.py: Chromium's ZipBuilder main class goes into the jar.
        classes = os.path.join(d, 'zipbuilder')
        java = os.path.join(src, TOOLS, 'signflinger/java/src/org/chromium/build/ZipBuilder.java')
        run([os.path.join(src, 'third_party/jdk/current/bin/javac'), '--release', '17',
             '-cp', out, '-d', classes, java])
        with zipfile.ZipFile(out, 'a', zipfile.ZIP_DEFLATED) as z:
            for root, _, names in sorted(os.walk(classes)):
                for n in sorted(names):
                    p = os.path.join(root, n)
                    z.write(p, os.path.relpath(p, classes))
    print(f"java_tools: {rel} <- {tool['group']}:{tool['artifact']}:{tool['version']} "
          f"jar-with-dependencies ({os.path.getsize(out)} bytes)")


def signflinger_jar_only(src):
    """zipbuilder.py runs signflinger.jar; the GN inputs drop the binary."""
    sub_once(os.path.join(src, 'build/android/gyp/util/zipbuilder.py'),
             r'^def _can_use_binary\(\):\n',
             'def _can_use_binary():\n    return False  # F-Droid build: no GraalVM native image\n')
    gni = os.path.join(src, 'build/config/android/internal_rules.gni')
    s = open(gni).read()
    s, n = re.subn(r'^\s*_signflinger_binary_path,\n', '', s, flags=re.M)
    s, m = re.subn(r'^_signflinger_binary_path =\n\s*"[^"]+"\n', '', s, flags=re.M)
    if n < 1 or m != 1:
        sys.exit(f'{gni}: signflinger binary references not found ({n}, {m})')
    with open(gni, 'w') as f:
        f.write(s)


def ijar(src, work):
    pb = open(os.path.join(src, TOOLS, 'bazel_tools/3pp/3pp.pb')).read()
    version = re.search(r'op: EQ\s+val: "([^"]+)"', pb)[1]
    d = os.path.join(work, 'bazel')
    run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--sparse', '-b', version,
         'https://github.com/bazelbuild/bazel.git', d])
    run(['git', '-C', d, 'sparse-checkout', 'set', 'third_party/ijar', 'src/main/cpp/util'])
    out = os.path.join(src, TOOLS, 'bazel_tools/cipd/ijar')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    srcs = [f'third_party/ijar/{n}.cc' for n in
            ('ijar', 'classfile', 'zip', 'mapped_file_unix', 'zlib_client', 'platform_utils')]
    srcs += [f'src/main/cpp/util/{n}.cc' for n in
             ('file', 'file_posix', 'path', 'path_posix', 'errors_posix', 'logging', 'strings', 'numbers')]
    # Newer g++ no longer includes <cstring> through <string>.
    run([os.environ.get('CXX', 'g++'), '-O2', '-std=c++17', '-include', 'cstring', '-I.', '-o', out]
        + srcs + ['-lz'], cwd=d)
    print(f'java_tools: bazel_tools/cipd/ijar from Bazel {version} third_party/ijar')


def dx(src, work):
    pb = open(os.path.join(src, 'third_party/aosp_dalvik/3pp/3pp.pb')).read()
    url = re.search(r'download_url: "([^"]+)"', pb)[1]
    d = os.path.join(work, 'dalvik')
    os.makedirs(d)
    tgz = os.path.join(work, 'dalvik.tar.gz')
    with open(tgz, 'wb') as f:
        f.write(fetch(url))
    with tarfile.open(tgz) as t:
        t.extractall(d, members=[m for m in t.getmembers() if m.name.startswith('dx/src/')],
                     filter='data')
    javas = [os.path.join(r, n) for r, _, ns in os.walk(os.path.join(d, 'dx/src')) for n in ns
             if n.endswith('.java')]
    classes = os.path.join(d, 'out')
    jdk = os.path.join(src, 'third_party/jdk/current/bin')
    run([os.path.join(jdk, 'javac'), '-nowarn', '-d', classes, '--release', '11'] + sorted(javas))
    out = os.path.join(src, 'third_party/aosp_dalvik/cipd/lib/dx.jar')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run([os.path.join(jdk, 'jar'), 'cf', out, '-C', classes, '.'])
    print(f'java_tools: aosp_dalvik/cipd/lib/dx.jar from {url} ({len(javas)} sources)')


# AOSP platform/prebuilts/sdk: current/system/android.jar, the system API
# stubs AOSP's SDK build makes (Apache-2.0), at this commit of main.
PREBUILTS_SDK = 'https://android.googlesource.com/platform/prebuilts/sdk'
PREBUILTS_SDK_REVISION = '3af7c93524be6f51e092b87b17f009f13ee98b43'


def android_system(src, work):
    d = os.path.join(work, 'prebuilts-sdk')
    run(['git', 'init', '-q', d])
    run(['git', '-C', d, 'fetch', '-q', '--depth', '1', '--filter=blob:none', PREBUILTS_SDK,
         PREBUILTS_SDK_REVISION])
    run(['git', '-C', d, 'sparse-checkout', 'set', '--no-cone', '/current/system/android.jar'])
    run(['git', '-C', d, 'checkout', '-q', 'FETCH_HEAD'])
    out = os.path.join(src, 'third_party/android_system_sdk/cipd/android_system.jar')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.copyfile(os.path.join(d, 'current/system/android.jar'), out)
    print(f'java_tools: android_system_sdk/cipd/android_system.jar <- AOSP prebuilts/sdk '
          f'{PREBUILTS_SDK_REVISION[:12]} current/system/android.jar')


def main():
    src, pins_path = os.path.abspath(sys.argv[1]), sys.argv[2]
    tools = json.load(open(pins_path)).get('maven_tools', {})
    work = tempfile.mkdtemp(prefix='java-tools-')
    for name in MAVEN_TOOLS:
        tool = dict(tools.get(name) or {})
        if not tool.get('version'):
            sys.exit(f'java_tools: no {name} version in {pins_path} (run sync-trim.yml)')
        # CIPD's 3pp tags end in a hash of the version_deps (".2be7cec8ac").
        tool['version'] = re.sub(r'\.[0-9a-f]{10}$', '', tool['version'])
        maven_jar(src, name, tool, work)
    signflinger_jar_only(src)
    ijar(src, work)
    dx(src, work)
    android_system(src, work)
    shutil.rmtree(work)


if __name__ == '__main__':
    main()
