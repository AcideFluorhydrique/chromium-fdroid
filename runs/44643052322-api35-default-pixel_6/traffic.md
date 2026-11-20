## Network traffic per APK and phase

From Chromium's NetLog (every URL the browser requested, dated by the NetLog's own clock), and the emulator packet capture (DNS queries and TLS server names of the whole emulator, so other apps are included).

### fdroid

- **start-idle** (5): `clients2.google.com`, `edgedl.me.gvt1.com`, `fonts.gstatic.com`, `update.googleapis.com`, `www.google.com`
- **browse** (10): `auth.wikimedia.org`, `content-autofill.googleapis.com`, `en.wikipedia.org`, `example.com`, `fonts.gstatic.com`, `intake-analytics.wikimedia.org`, `meta.wikimedia.org`, `thumb.wikimedia.org`, `upload.wikimedia.org`, `www.google.com`
- **other** (2): `example.com`, `www.google.com`

### vanilla

- **start-idle** (5): `clients2.google.com`, `edgedl.me.gvt1.com`, `fonts.gstatic.com`, `update.googleapis.com`, `www.google.com`
- **browse** (8): `auth.wikimedia.org`, `content-autofill.googleapis.com`, `en.wikipedia.org`, `example.com`, `fonts.gstatic.com`, `thumb.wikimedia.org`, `upload.wikimedia.org`, `www.google.com`
- **other** (2): `example.com`, `www.google.com`

### Whole emulator capture (packet times 1795133263-1795133266)

`connectivitycheck.gstatic.com (dns)`, `g.co (dns)`, `g.co (tls)`, `remoteprovisioning.googleapis.com (dns)`, `remoteprovisioning.googleapis.com (tls)`, `time.android.com (dns)`, `www.google.com (dns)`, `www.google.com (tls)`

