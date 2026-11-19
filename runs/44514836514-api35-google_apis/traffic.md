## Network traffic per APK and phase

From Chromium's NetLog (every URL the browser requested, dated by the NetLog's own clock), and the emulator packet capture (DNS queries and TLS server names of the whole emulator, so other apps are included).

### fdroid

- **start-idle** (5): `clients2.google.com`, `edgedl.me.gvt1.com`, `update.googleapis.com`, `www.google.com`, `www.googleapis.com`
- **browse** (8): `auth.wikimedia.org`, `content-autofill.googleapis.com`, `en.wikipedia.org`, `example.com`, `intake-analytics.wikimedia.org`, `thumb.wikimedia.org`, `upload.wikimedia.org`, `www.google.com`
- **other** (2): `example.com`, `www.google.com`

### Whole emulator capture (packet times 1795087701-1795087701)

`connectivitycheck.gstatic.com (dns)`, `www.google.com (dns)`, `www.google.com (tls)`

