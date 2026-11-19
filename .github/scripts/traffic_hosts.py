#!/usr/bin/env python3
"""List the hosts an APK connects to, from the emulator's packet capture and
Chromium's NetLog, per test phase.

Usage: traffic_hosts.py <traffic.pcap> <results dir>

<results dir> holds one directory per APK label, each with phases.tsv
("phase<TAB>start<TAB>end", host epoch seconds, written by emulator_test.py)
and optionally netlog.json. Writes traffic.md into <results dir> and
<label>/hosts.tsv for each label.

From the capture: DNS queries (UDP port 53) and the server name (SNI) of TLS
ClientHellos on TCP. QUIC hides its SNI, but its DNS lookup is still seen.
From the NetLog: every URL the browser requested, which also covers DNS over
HTTPS and connection reuse. The capture covers the whole emulator, so other
apps' traffic in the same time window is included; with target=default (AOSP)
there is little of it.
"""

import collections
import json
import os
import re
import struct
import sys


def packets(path):
    with open(path, 'rb') as f:
        head = f.read(24)
        if len(head) < 24:
            return
        magic = head[:4]
        if magic in (b'\xd4\xc3\xb2\xa1', b'\x4d\x3c\xb2\xa1'):
            end = '<'
        elif magic in (b'\xa1\xb2\xc3\xd4', b'\xa1\xb2\x3c\x4d'):
            end = '>'
        else:
            sys.exit(f'{path}: not a pcap file')
        nano = magic in (b'\x4d\x3c\xb2\xa1', b'\xa1\xb2\x3c\x4d')
        linktype = struct.unpack(end + 'I', head[20:24])[0]
        while True:
            rec = f.read(16)
            if len(rec) < 16:
                return
            sec, frac, incl, _ = struct.unpack(end + 'IIII', rec)
            data = f.read(incl)
            yield sec + frac / (1e9 if nano else 1e6), linktype, data


def ip_payload(linktype, data):
    """(proto, src, dst, payload) of an IPv4 packet, or None."""
    if linktype == 1:  # Ethernet
        if len(data) < 14 or data[12:14] != b'\x08\x00':
            return None
        data = data[14:]
    elif linktype == 113:  # Linux cooked
        if len(data) < 16 or data[14:16] != b'\x08\x00':
            return None
        data = data[16:]
    elif linktype not in (101, 228):  # raw IP
        return None
    if len(data) < 20 or data[0] >> 4 != 4:
        return None
    ihl = (data[0] & 15) * 4
    return data[9], data[12:16], data[16:20], data[ihl:]


def dns_name(msg, off):
    labels = []
    for _ in range(64):
        if off >= len(msg):
            return None
        n = msg[off]
        if n == 0:
            return '.'.join(labels).lower()
        if n & 0xC0:
            return None
        labels.append(msg[off + 1:off + 1 + n].decode('ascii', 'replace'))
        off += 1 + n
    return None


def dns_query(udp):
    if len(udp) < 8 + 12:
        return None
    sport, dport = struct.unpack('>HH', udp[:4])
    if dport != 53:
        return None
    msg = udp[8:]
    if msg[2] & 0x80 or struct.unpack('>H', msg[4:6])[0] < 1:
        return None
    return dns_name(msg, 12)


def tls_sni(tcp):
    if len(tcp) < 20:
        return None
    off = (tcp[12] >> 4) * 4
    p = tcp[off:]
    # TLS record: handshake (22), ClientHello (1)
    if len(p) < 43 or p[0] != 22 or p[5] != 1:
        return None
    i = 5 + 4 + 2 + 32
    try:
        i += 1 + p[i]                                  # session id
        i += 2 + struct.unpack('>H', p[i:i + 2])[0]     # cipher suites
        i += 1 + p[i]                                  # compression
        end = i + 2 + struct.unpack('>H', p[i:i + 2])[0]
        i += 2
        while i + 4 <= min(end, len(p)):
            typ, ln = struct.unpack('>HH', p[i:i + 4])
            if typ == 0:
                j = i + 4 + 2
                if p[j] == 0:
                    n = struct.unpack('>H', p[j + 1:j + 3])[0]
                    return p[j + 3:j + 3 + n].decode('ascii', 'replace').lower()
            i += 4 + ln
    except (IndexError, struct.error):
        return None
    return None


def netlog_hosts(path, phases):
    """{phase: Counter(host)} for the URLs in a (possibly truncated) NetLog.

    Each event's "time" is in ms since constants.timeTickOffset (epoch ms);
    an event's params come before its time, so a URL is dated by the next
    "time" after it. URLs outside every phase go under "other"."""
    try:
        text = open(path, errors='replace').read()
    except OSError:
        return {}
    m = re.search(r'"timeTickOffset":"?(\d+)', text)
    offset = int(m[1]) / 1000 if m else None
    out = collections.defaultdict(collections.Counter)
    for m in re.finditer(r'"(?:url|original_url)":"(?:https?|wss?)://([^/":?]+)', text):
        host = m[1].lower()
        t = re.compile(r'"time":"(\d+)"').search(text, m.end())
        phase = 'other'
        if t and offset is not None:
            ts = offset + int(t[1]) / 1000
            phase = next((n for n, s, e in phases if s <= ts <= e), 'other')
        out[phase][host] += 1
    return out


def main():
    pcap, results = sys.argv[1:3]
    phases = []  # (label, phase, start, end)
    labels = sorted(d for d in os.listdir(results) if os.path.isfile(os.path.join(results, d, 'phases.tsv')))
    for label in labels:
        for line in open(os.path.join(results, label, 'phases.tsv')):
            name, start, end = line.rstrip('\n').split('\t')
            phases.append((label, name, float(start), float(end)))

    seen = collections.defaultdict(collections.Counter)  # (label, phase) -> host -> count
    other = collections.Counter()
    times = []
    if os.path.exists(pcap):
        for ts, linktype, data in packets(pcap):
            ip = ip_payload(linktype, data)
            if not ip:
                continue
            proto, _, _, payload = ip
            host = None
            if proto == 17:
                host = dns_query(payload)
                kind = 'dns'
            elif proto == 6:
                host = tls_sni(payload)
                kind = 'tls'
            if not host:
                continue
            times.append(ts)
            where = next(((l, n) for l, n, s, e in phases if s <= ts <= e), None)
            if where:
                seen[where][f'{host} ({kind})'] += 1
            else:
                other[f'{host} ({kind})'] += 1

    lines = ['## Network traffic per APK and phase', '',
             "From Chromium's NetLog (every URL the browser requested, dated by the "
             'NetLog\'s own clock), and the emulator packet capture (DNS queries and TLS '
             'server names of the whole emulator, so other apps are included).', '']
    for label in labels:
        lines += [f'### {label}', '']
        own = [(n, s, e) for l, n, s, e in phases if l == label]
        net = netlog_hosts(os.path.join(results, label, 'netlog.json'), own)
        rows = [(f'netlog:{p}', h, c) for p, hosts in net.items() for h, c in hosts.items()]
        for (l, phase), hosts in seen.items():
            if l == label:
                rows += [(f'capture:{phase}', h, c) for h, c in hosts.items()]
        with open(os.path.join(results, label, 'hosts.tsv'), 'w') as f:
            f.write('source\thost\tcount\n')
            f.writelines(f'{p}\t{h}\t{c}\n' for p, h, c in sorted(rows))
        for phase in [n for n, s, e in own] + ['other']:
            hs = sorted(net.get(phase, {}))
            if phase == 'other' and not hs:
                continue
            lines.append(f'- **{phase}** ({len(hs)}): ' + (', '.join(f'`{h}`' for h in hs) or 'none'))
        lines.append('')
    allcap = sorted(set(other) | {h for hosts in seen.values() for h in hosts})
    if allcap:
        span = f'{min(times):.0f}-{max(times):.0f}' if times else '?'
        lines += [f'### Whole emulator capture (packet times {span})', '',
                  ', '.join(f'`{h}`' for h in allcap), '']
    text = '\n'.join(lines) + '\n'
    with open(os.path.join(results, 'traffic.md'), 'w') as f:
        f.write(text)
    print(text)


if __name__ == '__main__':
    main()
