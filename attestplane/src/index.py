"""
attestplane Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/attestplane/

Uses: from attestplane import EventDraft, hash_event
"""

import sys
import json
from js import Response, Headers

# ── Dynamic module loading for Workers ───────────────────────────────────────
sys.path.insert(0, "./python_modules")

try:
    from attestplane import EventDraft, hash_event
    package_loaded = True
    load_error = None
except Exception as e:
    package_loaded = False
    load_error = str(e)


# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

LLMS_TXT = """# attestplane Demo API

> Live demo API and UI for the `attestplane` package on Cloudflare Workers, providing ways to create EventDrafts and compute their hashes.

## Deployment Details
- **Demo URL**: https://attestplane.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/attestplane
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoints

### `GET /api/info`
Returns general metadata about the attestplane package version running.

### `POST /api/hash_event`
Computes the hash of a given event draft.

#### Request Body
- `event_type` (string, required): Event type string.
- `actor` (string, required): The actor creating the event.
- `payload` (object, optional): Event payload.

#### Response Body
- `hash` (string): The computed hash.
- `event` (object): The event details.
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🛩️</text></svg>"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML UI
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>attestplane Demo · Cloudflare Python Worker</title>
  <meta name="description" content="Live demo of the attestplane PyPI package running as a Cloudflare Python Worker.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:        #0f172a;
      --surface:   #1e293b;
      --surface2:  #334155;
      --border:    rgba(255,255,255,0.1);
      --accent:    #38bdf8;
      --accent2:   #818cf8;
      --green:     #34d399;
      --text:      #f8fafc;
      --muted:     #94a3b8;
      --radius:    12px;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

    /* ── Gradient orbs ── */
    .orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
    .orb  { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.4; }
    .orb-1 { width: 600px; height: 600px; background: radial-gradient(circle, #38bdf866, transparent 65%); top: -200px; left: -100px; animation: drift 20s ease-in-out infinite alternate; }
    .orb-2 { width: 500px; height: 500px; background: radial-gradient(circle, #818cf855, transparent 65%); bottom: -150px; right: -100px; animation: drift 25s ease-in-out infinite alternate-reverse; }

    @keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(30px,40px) scale(1.05); } }

    /* ── Layout ── */
    .container { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 0 24px; }

    /* ── Header ── */
    header { padding: 30px 0 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .badge { border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 700; letter-spacing: 0.04em; }
    .badge-cf  { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; }
    .badge-pypi { border: 1px solid var(--border); color: var(--muted); text-decoration: none; transition: all .2s; }
    .badge-pypi:hover { border-color: var(--accent); color: var(--accent); }

    /* ── Hero ── */
    .hero { padding: 60px 0 40px; text-align: center; }
    h1 { font-size: clamp(36px, 6vw, 64px); font-weight: 800; line-height: 1.1; margin-bottom: 16px; background: linear-gradient(135deg, #fff, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    h1 span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { font-size: 18px; color: var(--muted); max-width: 600px; margin: 0 auto; line-height: 1.6; }

    /* ── Main Card ── */
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 40px; }
    .card-header { padding: 16px 24px; border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 600; color: var(--muted); display: flex; justify-content: space-between; }
    .card-body { padding: 24px; }

    .form-group { margin-bottom: 20px; }
    label { display: block; font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }
    input[type="text"], textarea { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 12px; color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 14px; outline: none; transition: border-color .2s; }
    input[type="text"]:focus, textarea:focus { border-color: var(--accent); }
    textarea { resize: vertical; min-height: 100px; }

    .btn { display: inline-block; width: 100%; padding: 14px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border: none; border-radius: 8px; color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform .2s, box-shadow .2s; text-align: center; font-family: 'Inter', sans-serif; }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(56,189,248,.3); }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }

    .result-box { margin-top: 24px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: var(--green); word-break: break-all; display: none; }
    .result-box.show { display: block; animation: fadeUp .3s ease; }
    .error-box { color: #f87171; }

    @keyframes fadeUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }

    /* ── API Snippets ── */
    .section-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center; }
    .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; }
    .api-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
    .api-card h3 { font-size: 15px; margin-bottom: 10px; color: var(--accent); }
    pre { background: var(--bg); padding: 12px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 12px; overflow-x: auto; color: #e2e8f0; }

    /* ── Footer ── */
    footer { border-top: 1px solid var(--border); padding: 30px 0; text-align: center; color: var(--muted); font-size: 13px; margin-bottom: 20px; }
    footer a { color: var(--accent); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
    .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.2); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; vertical-align: middle; margin-right: 8px; }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
  </div>

  <div class="container">
    <header>
      <div>
        <span class="badge badge-cf">⚡ Cloudflare Python Worker</span>
        <a href="https://pypi.rosetraviss.uk/attestplane" class="badge badge-pypi" target="_blank" rel="noopener">📦 pip install attestplane</a>
      </div>
      <div id="pkg-status" style="font-size:13px;font-family:'JetBrains Mono',monospace;color:var(--muted)">Checking status...</div>
    </header>

    <section class="hero">
      <h1>attest<span>plane</span></h1>
      <p class="hero-sub">Live demo of the <code>attestplane</code> package in Pyodide. Create EventDrafts and compute cryptographic hashes.</p>
    </section>

    <section>
      <div class="card">
        <div class="card-header">
          <span>EventDraft Hash Calculator</span>
          <span>hash_event(event)</span>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="event-type">Event Type</label>
            <input type="text" id="event-type" value="EVAL_EVENT" placeholder="e.g., EVAL_EVENT">
          </div>
          <div class="form-group">
            <label for="event-actor">Actor</label>
            <input type="text" id="event-actor" value="alice@example.com" placeholder="e.g., user@domain.com">
          </div>
          <div class="form-group">
            <label for="event-payload">Payload (JSON)</label>
            <textarea id="event-payload">{"score_pct": 95, "model": "gpt-4"}</textarea>
          </div>
          <button class="btn" id="hash-btn" onclick="computeHash()">Compute Hash</button>

          <div id="result" class="result-box"></div>
        </div>
      </div>
    </section>

    <section>
      <h2 class="section-title">Library Usage</h2>
      <div class="api-grid">
        <div class="api-card">
          <h3>Create EventDraft</h3>
          <pre>from attestplane import EventDraft

draft = EventDraft(
    event_type="EVAL_EVENT",
    actor="alice@example.com",
    payload={"score_pct": 95}
)</pre>
        </div>
        <div class="api-card">
          <h3>Hash Event</h3>
          <pre>from attestplane import hash_event

event_hash = hash_event(draft)
print(event_hash.hex())</pre>
        </div>
      </div>
    </section>

    <footer>
      Using <a href="https://pypi.rosetraviss.uk/attestplane" target="_blank">attestplane</a> PyPI package ·
      Runs on <a href="https://developers.cloudflare.com/workers/languages/python/" target="_blank">Cloudflare Python Workers</a> ·
      Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
    </footer>
  </div>

  <script>
    async function init() {
      try {
        const res = await fetch('/api/info');
        const data = await res.json();
        const statusEl = document.getElementById('pkg-status');
        if (data.loaded) {
          statusEl.innerHTML = `<span style="color:var(--green)">●</span> v${data.version}`;
        } else {
          statusEl.innerHTML = `<span style="color:#f87171">●</span> Load Error`;
          console.error(data.error);
        }
      } catch (e) {
        document.getElementById('pkg-status').innerText = 'Error loading metadata';
      }
    }

    async function computeHash() {
      const btn = document.getElementById('hash-btn');
      const resBox = document.getElementById('result');

      const type = document.getElementById('event-type').value.trim();
      const actor = document.getElementById('event-actor').value.trim();
      let payload = {};

      try {
        payload = JSON.parse(document.getElementById('event-payload').value);
      } catch (e) {
        resBox.className = 'result-box show error-box';
        resBox.textContent = 'Invalid JSON in payload field.';
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Computing...';

      try {
        const res = await fetch('/api/hash_event', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ event_type: type, actor: actor, payload: payload })
        });
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        resBox.className = 'result-box show';
        resBox.innerHTML = `<strong>Hash:</strong><br>${data.hash}<br><br><strong>Draft Details:</strong><br><pre style="background:none;padding:0">${JSON.stringify(data.event, null, 2)}</pre>`;
      } catch (e) {
        resBox.className = 'result-box show error-box';
        resBox.textContent = `Error: ${e.message}`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Compute Hash';
      }
    }

    init();
  </script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# API Helpers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-store",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

# ─────────────────────────────────────────────────────────────────────────────
# Route Handlers
# ─────────────────────────────────────────────────────────────────────────────

async def handle_info():
    version = "unknown"
    if package_loaded:
        try:
            import importlib.metadata
            version = importlib.metadata.version("attestplane")
        except Exception:
            pass

    return json_response({
        "loaded": package_loaded,
        "error": load_error,
        "version": version
    })

async def handle_hash_event(request):
    if not package_loaded:
        return json_response({"error": f"Package not loaded: {load_error}"}, status=500)

    try:
        body = await request.json()
        if body is None:
            body_dict = {}
        elif hasattr(body, 'to_py'):
            body_dict = body.to_py()
        elif isinstance(body, dict):
            body_dict = body
        else:
            body_dict = {}

        if not isinstance(body_dict, dict):
            return json_response({"error": "Invalid request body format. Expected a JSON object."}, status=400)

        event_type = body_dict.get("event_type", "UNKNOWN")
        actor = body_dict.get("actor", "anonymous")
        payload = body_dict.get("payload", {})

        draft = EventDraft(event_type=event_type, actor=actor, payload=payload)
        h = hash_event(draft)

        return json_response({
            "hash": h.hex(),
            "event": {
                "event_type": draft.event_type,
                "actor": draft.actor,
                "payload": draft.payload
            }
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=400)


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    from urllib.parse import urlparse
    path = urlparse(request.url).path or "/"

    if request.method == "OPTIONS":
        headers = Headers.new({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }.items())
        return Response.new("", headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()

    if path == "/api/hash_event" and request.method == "POST":
        return await handle_hash_event(request)

    if path == "/":
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)

    return Response.new("Not Found", status=404)
