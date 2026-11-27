#!/usr/bin/env python3
"""Install Android SDK packages with F-Droid's sdkmanager.

Usage: sdk_install.py <sdk dir> <package>...    e.g. "platforms;android-37.2"

Same as `ANDROID_HOME=<sdk dir> sdkmanager <package>...`, except for SDK
platforms, which some sdkmanager versions skip because Google's package
metadata is broken:
platform-37.2_r02.zip says Platform.Version=${PLATFORM_VERSION}, so
sdkmanager has no "platforms;android-37.2". Those are taken from the same
checksums.json sdkmanager uses (F-Droid's Android SDK transparency log, its
signature checked by sdkmanager with gpgv), and the zip's sha256 must match.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

import sdkmanager  # F-Droid's (Debian package sdkmanager)

REPO = 'https://dl.google.com/android/repository/'


def platform_url(checksums, api):
    """Newest release of platform-<api>_rNN.zip in the transparency log."""
    found = []
    for url in checksums:
        m = re.fullmatch(re.escape(REPO) + rf'platform-{re.escape(api)}_r(\d+)\.zip', url)
        if m:
            found.append((int(m[1]), url))
    return max(found)[1] if found else None


def main():
    sdk = Path(sys.argv[1]).resolve()
    sdk.mkdir(parents=True, exist_ok=True)
    sdkmanager.build_package_list(use_net=True)
    checksums = json.loads((sdkmanager.get_cachedir() / 'checksums.json').read_text())
    for package in sys.argv[2:]:
        m = re.fullmatch(r'platforms;android-([0-9.]+)', package)
        if not m:
            sdkmanager.install(package, sdk)
            continue
        # Platforms always this way, so every sdkmanager version installs the
        # same (newest) release; older ones lack the broken-metadata ones.
        url = m and platform_url(checksums, m[1])
        if not url:
            sys.exit(f'sdk_install: {package} is not in F-Droid\'s Android SDK transparency log')
        install_dir = sdk / 'platforms' / f'android-{m[1]}'
        if install_dir.exists():
            continue
        zipball = sdkmanager.get_cachedir() / url.rsplit('/', 1)[1]
        sdkmanager.download_file(url, zipball)
        sha = hashlib.sha256(zipball.read_bytes()).hexdigest()
        if sha not in {e['sha256'] for e in checksums[url]}:
            zipball.unlink()
            sys.exit(f'sdk_install: {url}: sha256 {sha} is not the one in the transparency log')
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        sdkmanager._install_zipball_from_cache(zipball, install_dir)
        try:
            sdkmanager._generate_package_xml(install_dir, package, url)
        except Exception as e:  # only metadata for other SDK tools
            print(f'sdk_install: no package.xml for {package}: {e}')
        print(f'sdk_install: {package} from {url} (sha256 {sha[:16]}, as in the transparency log)')


if __name__ == '__main__':
    main()
