# cf-tracker 📍

A fake Cloudflare CAPTCHA page that silently collects everything it can about whoever opens the link. Built for a cybersecurity class to demonstrate how much data a single page visit can expose — no special permissions, no installs, no warning.

---

## What it collects

**Location**
- GPS coordinates with accuracy in meters (asks permission on mobile)
- IP-based geolocation fallback — no permission needed
- Direct Google Maps link to their location

**IP Intelligence**
- ISP, organization, ASN
- Region, city, ZIP code, timezone
- VPN/proxy detection
- Mobile vs datacenter detection
- Real IP chain via X-Forwarded-For headers

**WebRTC IP Leak**
- Exposes the victim's real local IP address even if they're behind a VPN
- Same technique used by VPN leak checker sites

**Browser Fingerprint**
- Canvas fingerprint — unique per GPU/driver/OS combo, survives incognito
- Audio fingerprint — AudioContext hash, used by banks for fraud detection
- WebGL GPU model and vendor
- Screen resolution, pixel ratio, color depth
- CPU core count, device memory
- Touch points (reveals mobile vs desktop)
- Installed fonts (28 checked — narrows down OS and software)
- Browser plugins, language, timezone, cookie status, Do Not Track

**Device & Hardware**
- Camera count, microphone count, speaker count
- Accelerometer/motion data on mobile — no permission needed
- Battery level and charging status
- Network type (4G/WiFi), download speed, RTT latency

**Session & Behaviour**
- Unique session ID per visitor
- Tracks repeat visits and flags returning visitors
- Tab visibility events — logs every time they switch away and come back
- Browser history depth

**Server-side Headers**
- Accept-Language, Accept-Encoding, Referer, Origin — captured without any JS

---

## Example output

```
╔════════════════════════════════════════════════════════════╗
║  PING #1  21:10:10  via GPS  Session: ...a3f9c2b1  [NEW VISITOR]  ║
╚════════════════════════════════════════════════════════════╝

  [ LOCATION ]
    LAT/LNG    : xx.xxxxxx, xx.xxxxxx
    ACCURACY   : ±5m  ← GPS precision!
    GOOGLE MAP : https://maps.google.com/?q=xx.xxxxxx,xx.xxxxxx

  [ IP DATABASE ]
    ADDRESS    : xxx.xxx.xxx.xxx
    ISP        : Your ISP
    ASN        : AS##### Your ISP
    REGION     : Region, Country
    ZIP        : xxxxx
    TIMEZONE   : Continent/City
    MOBILE     : No
    VPN/PROXY  : No
    HOSTING    : No

  [ WEBRTC IP LEAK ]  ← real IPs even behind VPN!
    192.168.x.x

  [ BROWSER FINGERPRINT ]
    PLATFORM   : iPhone / Apple Computer, Inc.
    SCREEN     : 390×844 @3x  depth:32bit
    LANGUAGE   : nl-NL  (nl-NL, nl, en)
    CPU CORES  : 6
    TOUCH PTS  : 5  ← mobile device
    GPU        : Apple A15 GPU
    CANVAS     : ...unique_hash_here
    AUDIO FP   : 142.894731  ← unique per device
    BATTERY    : 87% (charging)
    CAMERAS    : 2  MICS: 1  SPEAKERS: 1
    MOTION     : x=0.021 y=-0.134 z=9.812  ← accelerometer
    TAB EVENTS : 1 event(s)
```

---

## Setup

You need Python 3 and [ngrok](https://ngrok.com) (free).

```bash
# Terminal 1 — start the server
python server.py

# Terminal 2 — expose it to the internet
ngrok http 5000
```

Copy the `https://xxxx.ngrok-free.app` URL and send it. The page auto-runs the moment it loads — no interaction needed from the victim.

All data is printed to the terminal in real time and saved permanently to `tracker_log.txt`.

---

## Why this is interesting for a class

Every single thing this collects is done through standard browser APIs — nothing exotic, nothing that requires a vulnerability. This is just what a normal webpage can do.

The key takeaways:

- **WebRTC leaks your real IP even through a VPN** — most people don't know this
- **Canvas and audio fingerprints survive incognito mode** — clearing cookies doesn't help
- **IP geolocation is city-level at best** — GPS is the only way to get precision
- **Your GPU, fonts and screen reveal your exact device** — combined these create a unique ID
- **Accelerometer fires on mobile without any permission prompt** — completely silent

This is how ad networks track you across sites, how fraud detection works, and how phishing pages harvest recon before an attack.

---

> For educational and authorized use only. Don't be evil.
