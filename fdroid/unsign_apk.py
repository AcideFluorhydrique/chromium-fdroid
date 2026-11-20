#!/usr/bin/env python3
"""Write an unsigned copy of an APK, for F-Droid to sign.

Usage: unsign_apk.py <signed.apk> <unsigned.apk>

Chromium signs ChromePublic.apk with its debug key. The copy leaves out the
v1 signature files in META-INF and the APK Signing Block (v2/v3), which sits
between the entries and the central directory and is not a zip entry, so
rewriting the entries drops it. Entries keep their compression; stored
entries keep the alignment zipalign gives them (16 KiB for native libraries,
which Android maps straight from the APK, 4 bytes for the rest), padded with
an extra field the way zipalign does.
"""

import re
import struct
import sys
import zipfile

V1_SIGNATURE = re.compile(r'^META-INF/([^/]+\.(SF|RSA|DSA|EC)|MANIFEST\.MF)$')
LOCAL_HEADER = 30


def alignment(info):
    if info.compress_type != zipfile.ZIP_STORED:
        return 1
    return 16384 if info.filename.endswith('.so') else 4


def main():
    src, dst = sys.argv[1:3]
    dropped = 0
    with zipfile.ZipFile(src) as zin, open(dst, 'wb') as raw:
        zout = zipfile.ZipFile(raw, 'w')
        for info in zin.infolist():
            if V1_SIGNATURE.match(info.filename):
                dropped += 1
                continue
            data = zin.read(info)
            out = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            out.compress_type = info.compress_type
            out.external_attr = info.external_attr
            out.create_system = info.create_system
            align = alignment(info)
            extra = b''
            if align > 1:
                name_len = len(out.filename.encode('utf-8'))
                start = raw.tell() + LOCAL_HEADER + name_len
                pad = (-(start + 4)) % align  # 4 bytes of extra field header
                # Extra field 0xd935 is the one zipalign -p uses: alignment
                # as a uint16, then zero padding.
                pad_len = max(pad, 2)
                while (start + 4 + pad_len) % align:
                    pad_len += 1
                extra = struct.pack('<HHH', 0xd935, pad_len, align) + b'\0' * (pad_len - 2)
            out.extra = extra
            zout.writestr(out, data)
        zout.close()
    # Check: every stored entry is where alignment() wants it.
    with zipfile.ZipFile(dst) as z, open(dst, 'rb') as f:
        for info in z.infolist():
            f.seek(info.header_offset + 26)
            n, m = struct.unpack('<HH', f.read(4))
            data_start = info.header_offset + LOCAL_HEADER + n + m
            if data_start % alignment(info):
                sys.exit(f'{info.filename} is not aligned ({data_start})')
    print(f'{dst}: unsigned ({dropped} v1 signature files and the signing block dropped)')


if __name__ == '__main__':
    main()
