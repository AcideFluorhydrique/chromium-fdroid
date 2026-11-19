## Network traffic per APK and phase

From the emulator packet capture (DNS queries and TLS server names) and Chromium's NetLog (every URL the browser requested). The capture includes other apps active in the same window.

### fdroid

- **start-idle** (0): none
- **browse** (0): none
- **netlog** (11): `auth.wikimedia.org`, `clients2.google.com`, `content-autofill.googleapis.com`, `edgedl.me.gvt1.com`, `en.wikipedia.org`, `example.com`, `fonts.gstatic.com`, `thumb.wikimedia.org`, `update.googleapis.com`, `upload.wikimedia.org`, `www.google.com`

### Outside any test phase

`connectivitycheck.gstatic.com (dns)`, `g.co (dns)`, `g.co (tls)`, `remoteprovisioning.googleapis.com (dns)`, `remoteprovisioning.googleapis.com (tls)`, `time.android.com (dns)`, `www.google.com (dns)`, `www.google.com (tls)`

