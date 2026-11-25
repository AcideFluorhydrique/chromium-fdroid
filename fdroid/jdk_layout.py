#!/usr/bin/env python3
"""Lay out third_party/jdk/current from a system JDK the way Chromium's is.

Usage: jdk_layout.py <chromium src dir> <JDK home>

Chromium's JDK package (third_party/jdk/3pp/3pp.py, from Temurin) differs
from a stock JDK in two ways the build relies on: bin/java is a wrapper
running bin/java.chromium with -XX:+PerfDisableSharedMem (crbug.com/1441023),
and bin/javac-graalvm, a GraalVM native-image of javac, which
compile_java.py prefers on linux-x64. This makes third_party/jdk/current a
directory of symlinks into the given JDK (Debian's OpenJDK), adds the same
java wrapper, and makes compile_java.py run bin/javac, the path it takes on
every other host.
"""

import os
import re
import shutil
import sys

JAVA_WRAPPER = """#!/bin/sh

# https://crbug.com/1441023
exec "$0.chromium" -XX:+PerfDisableSharedMem "$@"
"""


def main():
    src, jdk = sys.argv[1], os.path.realpath(sys.argv[2])
    out = os.path.join(src, 'third_party/jdk/current')
    if os.path.islink(out) or os.path.isfile(out):
        os.remove(out)
    elif os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'bin'))
    for name in os.listdir(jdk):
        if name != 'bin':
            os.symlink(os.path.join(jdk, name), os.path.join(out, name))
    for name in os.listdir(os.path.join(jdk, 'bin')):
        target = os.path.join(jdk, 'bin', name)
        os.symlink(target, os.path.join(out, 'bin', name + '.chromium' if name == 'java' else name))
    with open(os.path.join(out, 'bin', 'java'), 'w') as f:
        f.write(JAVA_WRAPPER)
    os.chmod(os.path.join(out, 'bin', 'java'), 0o755)

    path = os.path.join(src, 'build/android/gyp/compile_java.py')
    s = open(path).read()
    new, n = re.subn(r"(    use_javac_graalvm = \()\n        sys\.platform == 'linux'\n",
                     r"\1\n        False  # F-Droid build: no GraalVM native-image javac\n        and sys.platform == 'linux'\n",
                     s)
    if n != 1:
        sys.exit(f'{path}: use_javac_graalvm not found')
    with open(path, 'w') as f:
        f.write(new)
    print(f'third_party/jdk/current: {jdk} with bin/java -> java.chromium wrapper; '
          'compile_java.py uses bin/javac')


if __name__ == '__main__':
    main()
