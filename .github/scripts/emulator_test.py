#!/usr/bin/env python3
"""Install a Chromium APK on a running emulator and screenshot a few screens.

Usage: emulator_test.py <apk> <label> <out dir>

Steps: install, skip the first-run screens, stay idle on about:blank for
IDLE_SECONDS (to see what a fresh install connects to on its own), open a page,
open Settings > Privacy and security (screenshot, scrolled), open an article
and try Reader mode (Simplified view), Settings again with the screen turned
90 degrees, then save logcat and Chromium's NetLog.
The start and end of each phase go to phases.tsv, for traffic_hosts.py. Screens are found with
`uiautomator dump`, so this does not depend on Chromium's internal activities.
"""

import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ARTICLE = 'https://en.wikipedia.org/wiki/Web_browser'
# Shorter when only screenshots matter (emulator.yml sets it to 20 without capture).
IDLE_SECONDS = int(os.environ.get('IDLE_SECONDS', '180'))


def adb(*args, check=False, timeout=180):
    r = subprocess.run(['adb', *args], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError(f'adb {" ".join(args)}: {r.stdout}{r.stderr}')
    return r.stdout


def shot(out, name):
    nodes()
    path = os.path.join(out, f'{name}.png')
    with open(path, 'wb') as f:
        f.write(subprocess.run(['adb', 'exec-out', 'screencap', '-p'], capture_output=True).stdout)
    print(f'screenshot {path}', flush=True)


def _nodes():
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


def nodes():
    """UI nodes, after dismissing system "isn't responding" dialogs (the AOSP image's
    launcher often hangs under emulation and its dialog covers the app)."""
    for _ in range(3):
        found = _nodes()
        if not any("isn't responding" in t for t, *_ in found):
            return found
        wait = [n for n in found if n[0] == 'Wait']
        if not wait:
            return found
        adb('shell', 'input', 'tap', str(wait[0][3]), str(wait[0][4]))
        print('dismissed an ANR dialog', flush=True)
        time.sleep(2)
    return _nodes()


_SIZE = []
_ROTATED = []


def screen():
    if not _SIZE:
        m = re.search(r'(\d+)x(\d+)', adb('shell', 'wm', 'size'))
        _SIZE.extend(map(int, m.groups()) if m else (1080, 2400))
    # `wm size` is the natural orientation; swap after rotate().
    return _SIZE[::-1] if _ROTATED else _SIZE


def rotate(on):
    """Turn the screen 90 degrees from its natural orientation (phone: landscape,
    tablet: portrait), or back."""
    adb('shell', 'settings', 'put', 'system', 'accelerometer_rotation', '0')
    adb('shell', 'settings', 'put', 'system', 'user_rotation', '1' if on else '0')
    _ROTATED[:] = [True] if on else []
    time.sleep(4)


_SCROLL_X = []


def scroll():
    """Swipe up, in the middle of the screen or over the open app menu."""
    w, h = screen()
    x = _SCROLL_X[0] if _SCROLL_X else w // 2
    adb('shell', 'input', 'swipe', str(x), str(h * 3 // 4), str(x), str(h // 3), '400')
    time.sleep(2)


def tap(*patterns, wait=3, tries=3, scrolls=0):
    """Tap the first node whose text, description or id matches one of patterns,
    scrolling down up to `scrolls` times to find it."""
    for attempt in range(tries + scrolls):
        if attempt >= tries:
            scroll()
        found = nodes()
        # Earlier patterns win, so a precise pattern can come before a loose one.
        for p in patterns:
            for text, desc, rid, x, y in found:
                if re.search(p, text, re.I) or re.search(p, desc, re.I) or re.search(p, rid, re.I):
                    adb('shell', 'input', 'tap', str(x), str(y))
                    print(f'tapped {p!r} ({text or desc or rid})', flush=True)
                    time.sleep(wait)
                    return True
        time.sleep(2)
    print(f'not found: {patterns}', flush=True)
    return False


def open_menu():
    # The button itself, not menu_button_wrapper / app_menu_button_container
    # around it (tapping those on tablets and in landscape did not open the menu).
    tap(r'^More options$', r'^Customize and control', r'id/menu_button$', r'menu_button')
    # On wide screens the menu is a short popup at the top right and Settings
    # is below its fold: scroll inside the popup, since a swipe in the middle
    # of the screen closes it.
    for text, desc, rid, x, y in nodes():
        if re.search(r'^(New tab|New Incognito tab|History|Bookmarks|Downloads)$', text):
            _SCROLL_X[:] = [x]
            break


SETTINGS_ACTIVITY = 'org.chromium.chrome.browser.settings.SettingsActivity'


def settings_activity(pkg):
    """Open Chromium's native Settings (the androidx preference screens with
    SlidingPaneLayout) directly. It is not exported, which adb root allows."""
    out = adb('shell', 'am', 'start', '-W', '-n', f'{pkg}/{SETTINGS_ACTIVITY}')
    print(f'settings activity: {out.strip()}', flush=True)
    time.sleep(4)
    return 'Error' not in out


def open_settings(pkg):
    open_menu()
    found = tap(r'^Settings$', scrolls=4)
    _SCROLL_X.clear()
    if not found:
        # The menu did not scroll far enough (seen on pixel_6): close it and
        # go straight to the Settings activity.
        adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
        time.sleep(1)
        found = settings_activity(pkg)
    return found


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
    # Root, to read the NetLog from the app's data directory afterwards.
    adb('root')
    adb('wait-for-device')
    print(adb('install', '-r', '-g', apk, timeout=600), flush=True)
    netlog = f'/data/data/{pkg}/netlog.json'
    # Chromium reads its command line from here when it is the debug app on a
    # debuggable system image; this skips the first-run screens and records
    # every network request in a NetLog.
    adb('shell', f'echo "_ --disable-fre --no-default-browser-check --no-first-run '
                 f'--log-net-log={netlog}" > /data/local/tmp/chrome-command-line')
    adb('shell', 'am', 'set-debug-app', '--persistent', pkg)

    phases = []
    t0 = time.time()
    launch(pkg, 'about:blank')
    time.sleep(25)
    skip_first_run()
    time.sleep(IDLE_SECONDS)
    phases.append(('start-idle', t0, time.time()))
    shot(out, '0-idle')

    t0 = time.time()
    launch(pkg, 'https://example.com')
    time.sleep(15)
    shot(out, '1-page')

    open_settings(pkg)
    shot(out, '2-settings')
    tap(r'^Privacy and security$', scrolls=2)
    shot(out, '3-privacy')
    scroll()
    shot(out, '4-privacy-scrolled')
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    time.sleep(1)
    tap(r'^Accessibility$', scrolls=4)
    tap(r'Simplified view', scrolls=3)
    shot(out, '5-accessibility')
    for _ in range(3):
        adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
        time.sleep(1)

    launch(pkg, ARTICLE)
    time.sleep(20)
    shot(out, '6-article')
    if tap(r'^View$', r'Simplified view', r'reader', wait=8, tries=3):
        shot(out, '7-reader-mode')

    # The same Settings screens turned 90 degrees: wide layouts (two panes,
    # SlidingPaneLayout) only show up above a certain width.
    launch(pkg, 'about:blank')
    time.sleep(5)
    rotate(True)
    open_settings(pkg)
    shot(out, '8-settings-rotated')
    tap(r'^Privacy and security$', scrolls=2)
    shot(out, '9-privacy-rotated')
    for _ in range(3):
        adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
        time.sleep(1)
    # On tablets the menu opens Settings in a tab; the native Settings screens
    # (where the SlidingPaneLayout clipping was) are shot here in both
    # orientations.
    for rotated in (True, False):
        rotate(rotated)
        suffix = '-rotated' if rotated else ''
        if settings_activity(pkg):
            shot(out, f'10-native-settings{suffix}')
            tap(r'^Privacy and security$', scrolls=2)
            shot(out, f'11-native-privacy{suffix}')
        for _ in range(3):
            adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
            time.sleep(1)

    phases.append(('browse', t0, time.time()))
    with open(os.path.join(out, 'phases.tsv'), 'w') as f:
        f.writelines(f'{n}\t{a:.3f}\t{b:.3f}\n' for n, a, b in phases)
    adb('shell', 'am', 'force-stop', pkg)
    time.sleep(2)
    data = subprocess.run(['adb', 'exec-out', 'cat', netlog], capture_output=True).stdout
    with open(os.path.join(out, 'netlog.json'), 'wb') as f:
        f.write(data)
    print(f'netlog: {len(data)} bytes', flush=True)

    # Straight to a file: on the tablet profiles `adb logcat -d` took longer
    # than two minutes to come back through a pipe.
    path = os.path.join(out, 'logcat.txt')
    with open(path, 'wb') as f:
        try:
            subprocess.run(['adb', 'logcat', '-d'], stdout=f, timeout=600)
        except subprocess.TimeoutExpired:
            print('logcat timed out, keeping what was read', flush=True)
    log = open(path, encoding='utf-8', errors='replace').read()
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
