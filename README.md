cf-tracker
A cybersecurity education demo that disguises itself as a Cloudflare Turnstile CAPTCHA and collects the visitor's GPS coordinates and IP-based location data.
Built for a cybersecurity class to demonstrate how tracking links work and how much information can be gathered from a single page visit.

How it works

Visitor opens the link and sees a fake Cloudflare "I am not a robot" verification page
The page silently attempts GPS location (asks permission on mobile)
If GPS is unavailable or denied, falls back to IP geolocation (no permission needed)
Coordinates, ISP, ASN, region, VPN status and more are sent to your local server
Every 10 minutes the location is pinged again automatically


What gets collected

GPS coordinates (if granted) with accuracy in meters
IP address
ISP and organization
ASN (Autonomous System Number)
Region, city and ZIP code
Timezone
Whether the user is on mobile, VPN/proxy, or hosting
Device platform and user agent
Direct Google Maps link to their location


Setup
Requirements

Python 3
ngrok (free at ngrok.com)

Run
Terminal 1 — start the server:
python server.py
Terminal 2 — expose it publicly:
ngrok http 5000
Copy the https://xxxx.ngrok-free.app URL and send it to your target.

Example output
[HH:MM:SS] PING #1 via GPS
  LAT      : xx.xxxxxx
  LNG      : xx.xxxxxx
  ACCURACY : +/-xxm
  PLATFORM : iPhone
  MAP      : https://maps.google.com/?q=xx.xxxxxx,xx.xxxxxx

[HH:MM:SS] PING #1 via IP
  LAT      : xx.xxxxxx
  LNG      : xx.xxxxxx
  LOCATION : City, Country
  IP       : xxx.xxx.xxx.xxx
  ── DATABASE LOOKUP ─────────────────
  ISP      : xxxxxxxxxx
  ORG      : xxxxxxxxxx
  ASN      : xxxxxxxxxx
  REGION   : Region, Country
  ZIP      : xxxxx
  TIMEZONE : Continent/City
  MOBILE   : False
  PROXY/VPN: False
  MAP      : https://maps.google.com/?q=xx.xxxxxx,xx.xxxxxx

Educational purpose
This project demonstrates:

How phishing/tracking links can be disguised as legitimate pages
The difference between GPS accuracy (~5m) vs IP geolocation (~city level)
How much data is publicly tied to an IP address (ISP, ASN, VPN detection)
Why browser location permissions exist and what they protect against


For educational and authorized testing use only.
