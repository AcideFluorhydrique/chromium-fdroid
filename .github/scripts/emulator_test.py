#!/usr/bin/env python3
"""Install a Chromium APK on a running emulator and screenshot a few screens.

Usage: emulator_test.py <apk> <label> <out dir>

Steps: install, skip the first-run screens, open a page, open
Settings > Privacy and security (screenshot, scrolled), open an article and
try Reader mode (Simplified view), then save logcat. Screens are found with
`uiautomator dump`, so this does not depend on Chromium's internal activities.
"""

import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ARTICLE = 'https://en.wikipedia.org/wiki/Web_browser'


def adb(*args, check=False, timeout=180):
    r = subprocess.run(['adb', *args], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError(f'adb {" ".join(args)}: {r.stdout}{r.stderr}')
    return r.stdout


def shot(out, name):
    path = os.path.join(out, f'{name}.png')
    with open(path, 'wb') as f:
        f.write(subprocess.run(['adb', 'exec-out', 'screencap', '-p'], capture_output=True).stdout)
    print(f'screenshot {path}', flush=True)


def nodes():
    adb('shell', 'uiautomator', 'dump', '/sdcard/ui.xml')
    xml = adb('shell', 'cat', '/sdcard/ui.xml')
    try:
        root = ET.fromstring(xml[xml.index('<?xml'):] if '<?xml' in xml else xml)
    except Exception:
        return []
    out = []
    for n in root.iter('node'):
        m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', n.get('bounds', ''))
        if m:
            x1, y1, x2, y2 = map(int, m.groups())
            out.append((n.get('text', ''), n.get('content-desc', ''), n.get('resource-id', ''),
                        (x1 + x2) // 2, (y1 + y2) // 2))
    return out


def tap(*patterns, wait=3, tries=3):
    """Tap the first node whose text, description or id matches one of patterns."""
    for _ in range(tries):
        for text, desc, rid, x, y in nodes():
            for p in patterns:
                if re.search(p, text, re.I) or re.search(p, desc, re.I) or re.search(p, rid, re.I):
                    adb('shell', 'input', 'tap', str(x), str(y))
                    print(f'tapped {p!r} ({text or desc or rid})', flush=True)
                    time.sleep(wait)
                    return True
        time.sleep(2)
    print(f'not found: {patterns}', flush=True)
    return False


def launch(pkg, url):
    """Open url in pkg by naming its launcher activity explicitly."""
    act = adb('shell', 'cmd', 'package', 'resolve-activity', '--brief', '-c',
              'android.intent.category.LAUNCHER', pkg).strip().splitlines()[-1]
    out = adb('shell', 'am', 'start', '-W', '-a', 'android.intent.action.VIEW', '-d', url, '-n', act)
    print(f'launch {act}: {out.strip()}', flush=True)


def skip_first_run():
    for _ in range(6):
        if not tap(r'^(Accept & continue|Use without an account|No thanks|Not now|Skip|Got it|Continue|Done)$',
                   r'(fre_|signin_fre_dismiss|negative_button)', wait=3, tries=1):
            break


_PIDS = {}


def pkg_pid(log, pkg, line):
    """Whether a logcat line comes from one of pkg's processes."""
    if pkg not in _PIDS:
        _PIDS[pkg] = set(re.findall(r'Start proc (\d+):' + re.escape(pkg), log))
    parts = line.split()
    return len(parts) > 2 and parts[2] in _PIDS[pkg]


def main():
    apk, label, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    aapt2 = sorted(__import__('glob').glob(os.path.expandvars('$ANDROID_HOME/build-tools/*/aapt2')))[-1]
    pkg = subprocess.run([aapt2, 'dump', 'packagename', apk], capture_output=True, text=True).stdout.strip()
    print(f'{label}: package {pkg}', flush=True)
    adb('logcat', '-c')
    print(adb('install', '-r', '-g', apk, timeout=600), flush=True)
    # Chromium reads its command line from here when it is the debug app on a
    # debuggable system image; this skips the first-run screens.
    adb('shell', 'echo "_ --disable-fre --no-default-browser-check --no-first-run" > /data/local/tmp/chrome-command-line')
    adb('shell', 'am', 'set-debug-app', '--persistent', pkg)

    launch(pkg, 'https://example.com')
    time.sleep(25)
    skip_first_run()
    shot(out, '1-page')

    tap(r'^More options$', r'^Customize and control', r'menu_button')
    tap(r'^Settings$')
    shot(out, '2-settings')
    tap(r'^Privacy and security$')
    shot(out, '3-privacy')
    adb('shell', 'input', 'swipe', '540', '1800', '540', '700', '400')
    time.sleep(2)
    shot(out, '4-privacy-scrolled')
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    time.sleep(1)
    tap(r'^Accessibility$')
    tap(r'Simplified view')
    shot(out, '5-accessibility')
    for _ in range(3):
        adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
        time.sleep(1)

    launch(pkg, ARTICLE)
    time.sleep(20)
    shot(out, '6-article')
    if tap(r'^View$', r'Simplified view', r'reader', wait=8, tries=3):
        shot(out, '7-reader-mode')

    log = adb('logcat', '-d', timeout=120)
    with open(os.path.join(out, 'logcat.txt'), 'w') as f:
        f.write(log)
    crashes = [l for l in log.splitlines()
               if 'FATAL EXCEPTION' in l or 'Fatal signal' in l or ('AndroidRuntime' in l and ' E ' in l)
               or (' F DEBUG' in l)]
    with open(os.path.join(out, 'summary.txt'), 'w') as f:
        f.write(f'{label}\npackage {pkg}\ncrash lines: {len(crashes)}\n' + '\n'.join(crashes[:40]) + '\n')
        gms = [l for l in log.splitlines() if pkg_pid(log, pkg, l) and re.search(r'GmsClient|GoogleApiManager|com\.google\.android\.gms', l)]
        f.write(f'lines from {pkg} mentioning Play services: {len(gms)}\n' + '\n'.join(gms[:40]) + '\n')
    print(open(os.path.join(out, 'summary.txt')).read(), flush=True)
    adb('uninstall', pkg)


if __name__ == '__main__':
    main()
