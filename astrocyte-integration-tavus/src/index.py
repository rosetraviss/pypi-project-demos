"""
Astrocyte Integration Tavus Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/astrocyte-integration-tavus/
"""

import json
import asyncio
from js import Response, Headers, fetch as js_fetch

# ── Real Astrocyte Integration Tavus package imports ─────────────────────────
import astrocyte_integration_tavus
from astrocyte_integration_tavus import TavusClient, TavusAPIError
import httpx

# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

LLMS_TXT = """# Astrocyte Integration Tavus Demo API

> Live demo API and UI for the `astrocyte-integration-tavus` package on Cloudflare Workers, providing a web interface to interact with the Tavus Conversational Video Interface.

## Deployment Details
- **Demo URL**: https://astrocyte-integration-tavus.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/astrocyte-integration-tavus
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoints

### `GET /api/info`
Returns general metadata about the installed library version.

### `GET /api/list_conversations`
List Tavus conversations. Requires providing an API key in the `Authorization` header.

#### Query Parameters
- `limit` (integer, optional)
- `page` (integer, optional)
- `status` (string, optional)

### `GET /api/get_conversation`
Get details for a specific Tavus conversation. Requires providing an API key in the `Authorization` header.

#### Query Parameters
- `conversation_id` (string, required): The ID of the conversation to fetch.
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🤖</text></svg>"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML UI
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Astrocyte Integration Tavus Demo</title>
  <meta name="description" content="Live demo of the astrocyte-integration-tavus PyPI package running as a Cloudflare Python Worker.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:        #0f172a;
      --surface:   #1e293b;
      --surface2:  #334155;
      --border:    rgba(255,255,255,0.1);
      --accent:    #8b5cf6;
      --accent2:   #ec4899;
      --blue:      #3b82f6;
      --green:     #10b981;
      --text:      #f8fafc;
      --muted:     #94a3b8;
      --radius:    14px;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

    /* ── Gradient orbs ── */
    .orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
    .orb  { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.2; }
    .orb-1 { width: 700px; height: 700px; background: radial-gradient(circle, #8b5cf666, transparent 65%); top: -250px; left: -150px; animation: drift 20s ease-in-out infinite alternate; }
    .orb-2 { width: 500px; height: 500px; background: radial-gradient(circle, #ec489955, transparent 65%); bottom: -150px; right: -100px; animation: drift 25s ease-in-out infinite alternate-reverse; }
    @keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(40px,50px) scale(1.12); } }

    /* ── Layout ── */
    .container { position: relative; z-index: 1; max-width: 1000px; margin: 0 auto; padding: 0 24px; }

    /* ── Header ── */
    header { padding: 28px 0 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .badge { border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 700; letter-spacing: 0.04em; }
    .badge-cf  { background: linear-gradient(135deg, #8b5cf6, #ec4899); color: #fff; }
    .badge-pypi { border: 1px solid var(--border); color: var(--muted); text-decoration: none; transition: all .2s; }
    .badge-pypi:hover { border-color: var(--accent); color: var(--accent); }

    /* ── Hero ── */
    .hero { padding: 60px 0 44px; text-align: center; }
    .live-tag { display: inline-flex; align-items: center; gap: 8px; background: rgba(139,92,246,.12); border: 1px solid rgba(139,92,246,.25); border-radius: 999px; padding: 6px 18px; font-size: 13px; color: var(--accent); font-weight: 600; margin-bottom: 24px; }
    .live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); animation: blink 2s ease-in-out infinite; }
    @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.2; } }
    h1 { font-size: clamp(32px, 5vw, 64px); font-weight: 800; line-height: 1.04; letter-spacing: -.03em; background: linear-gradient(140deg, #fff 0%, #9aa3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px; }
    h1 span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .hero-sub { font-size: 18px; color: var(--muted); max-width: 650px; margin: 0 auto 20px; line-height: 1.65; }

    /* ── Cards & Inputs ── */
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; margin-bottom: 30px; box-shadow: 0 12px 48px rgba(0,0,0,.45); }
    .card-header { padding: 18px 24px; border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; display: flex; align-items: center; justify-content: space-between; }
    .card-body { padding: 24px; }

    .input-group { margin-bottom: 20px; }
    .input-group label { display: block; font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
    .input-wrap { display: flex; background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: border-color .2s, box-shadow .2s; }
    .input-wrap:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(139,92,246,.12); }
    .input-wrap input { flex: 1; background: none; border: none; outline: none; color: var(--text); font-size: 15px; padding: 12px 16px; font-family: 'JetBrains Mono', monospace; }

    .btn { width: 100%; padding: 14px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border: none; border-radius: 10px; color: #fff; font-size: 15px; font-weight: 700; cursor: pointer; transition: all .2s; }
    .btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(139,92,246,.3); }
    .btn:active { transform: translateY(0); }
    .btn:disabled { opacity: .5; cursor: not-allowed; }

    .result-box { margin-top: 16px; padding: 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--green); white-space: pre-wrap; overflow-x: auto; display: none; }
    .result-box.show { display: block; animation: fadeUp .25s ease; }
    .result-box.error { color: #f87171; border-color: rgba(248,113,113,.2); }

    /* ── Footer ── */
    footer { border-top: 1px solid var(--border); padding: 30px 0; text-align: center; color: var(--muted); font-size: 13px; margin-top: 40px; }
    footer a { color: var(--accent); text-decoration: none; }
    footer a:hover { text-decoration: underline; }

    @keyframes fadeUp { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
    .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.2); border-top-color: #fff; border-radius: 50%; animation: spin .65s linear infinite; vertical-align: middle; margin-right: 7px; }
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
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span class="badge badge-cf">⚡ Cloudflare Python Worker</span>
        <a href="https://pypi.rosetraviss.uk/astrocyte-integration-tavus" class="badge badge-pypi" target="_blank" rel="noopener">
          📦 pip install astrocyte-integration-tavus
        </a>
      </div>
      <div style="font-size:12px;color:var(--muted);font-family:'JetBrains Mono',monospace" id="pkg-version"></div>
    </header>

    <section class="hero">
      <div class="live-tag"><div class="live-dot"></div> Live Tavus API · Pyodide Worker</div>
      <h1>astrocyte-integration-tavus</h1>
      <p class="hero-sub">
        Interact with the Tavus Conversational Video API directly from your browser. This worker uses the real Python package running via Pyodide.
      </p>
    </section>

    <!-- Global API Key -->
    <div class="card">
      <div class="card-header">1. Configuration</div>
      <div class="card-body">
        <div class="input-group">
          <label for="api-key">Tavus API Key (or type "demo" for mocked responses)</label>
          <div class="input-wrap">
            <input type="password" id="api-key" placeholder="Enter your Tavus API key...">
          </div>
        </div>
      </div>
    </div>

    <!-- List Conversations -->
    <div class="card">
      <div class="card-header">2. List Conversations <span>client.list_conversations()</span></div>
      <div class="card-body">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
          <div class="input-group">
            <label for="list-limit">Limit</label>
            <div class="input-wrap"><input type="number" id="list-limit" placeholder="10" value="10"></div>
          </div>
          <div class="input-group">
            <label for="list-status">Status</label>
            <div class="input-wrap"><input type="text" id="list-status" placeholder="active"></div>
          </div>
        </div>
        <button class="btn" id="btn-list" onclick="listConversations()">Fetch Conversations</button>
        <div class="result-box" id="res-list"></div>
      </div>
    </div>

    <!-- Get Conversation -->
    <div class="card">
      <div class="card-header">3. Get Conversation Details <span>client.get_conversation()</span></div>
      <div class="card-body">
        <div class="input-group">
          <label for="conv-id">Conversation ID</label>
          <div class="input-wrap"><input type="text" id="conv-id" placeholder="Enter conversation ID (e.g., c_123456)"></div>
        </div>
        <button class="btn" id="btn-get" onclick="getConversation()">Fetch Details</button>
        <div class="result-box" id="res-get"></div>
      </div>
    </div>

    <footer>
      <p>
        Using <a href="https://pypi.rosetraviss.uk/astrocyte-integration-tavus" target="_blank" rel="noopener">astrocyte-integration-tavus</a> PyPI package ·
        Runs on <a href="https://developers.cloudflare.com/workers/languages/python/" target="_blank" rel="noopener">Cloudflare Python Workers</a> (Pyodide/WASM) ·
        Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
      </p>
    </footer>
  </div>

  <script>
    async function init() {
      try {
        const res = await fetch('/api/info');
        const d = await res.json();
        document.getElementById('pkg-version').textContent = 'v' + (d.version || '0.1.0');
      } catch (e) {}
    }

    async function listConversations() {
      const btn = document.getElementById('btn-list');
      const resBox = document.getElementById('res-list');
      const apiKey = document.getElementById('api-key').value.trim();
      const limit = document.getElementById('list-limit').value;
      const status = document.getElementById('list-status').value;

      if (!apiKey) {
        showRes(resBox, 'Error: API Key is required.', true);
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>Fetching...';

      try {
        let url = `/api/list_conversations?limit=${limit}`;
        if (status) url += `&status=${status}`;

        const r = await fetch(url, { headers: { 'Authorization': `Bearer ${apiKey}` } });
        const data = await r.json();
        if (data.error) throw new Error(data.error);
        showRes(resBox, JSON.stringify(data.result, null, 2), false);
      } catch (e) {
        showRes(resBox, `Error: ${e.message}`, true);
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Fetch Conversations';
      }
    }

    async function getConversation() {
      const btn = document.getElementById('btn-get');
      const resBox = document.getElementById('res-get');
      const apiKey = document.getElementById('api-key').value.trim();
      const convId = document.getElementById('conv-id').value.trim();

      if (!apiKey) {
        showRes(resBox, 'Error: API Key is required.', true);
        return;
      }
      if (!convId) {
        showRes(resBox, 'Error: Conversation ID is required.', true);
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>Fetching...';

      try {
        const r = await fetch(`/api/get_conversation?conversation_id=${encodeURIComponent(convId)}`, {
          headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        const data = await r.json();
        if (data.error) throw new Error(data.error);
        showRes(resBox, JSON.stringify(data.result, null, 2), false);
      } catch (e) {
        showRes(resBox, `Error: ${e.message}`, true);
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Fetch Details';
      }
    }

    function showRes(el, text, isError) {
      el.textContent = text;
      el.className = 'result-box show' + (isError ? ' error' : '');
    }

    init();
  </script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-store",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

def parse_qs(url_str: str) -> dict:
    """Extract query parameters from a URL string."""
    query = {}
    if "?" in url_str:
        qs = url_str.split("?", 1)[1].split("#")[0]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query[k] = v
    return query


# ─────────────────────────────────────────────────────────────────────────────
# Pyodide httpx async transport
# ─────────────────────────────────────────────────────────────────────────────

class FetchAsyncTransport(httpx.AsyncBaseTransport):
    """
    A custom httpx AsyncTransport that uses Cloudflare Worker's js_fetch.
    This bypasses anyio/socket limitations in Pyodide.
    """
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        headers = dict(request.headers)

        # Read body if present
        body = await request.aread()

        req_kwargs = {
            "method": request.method,
            "headers": Headers.new(headers.items()),
        }
        if body:
            req_kwargs["body"] = body

        try:
            res = await js_fetch(url, req_kwargs)
        except Exception as e:
            raise httpx.ConnectError(f"js_fetch failed: {str(e)}") from e

        # Extract response text using text()
        text = await res.text()
        content = text.encode("utf-8")

        res_headers = []
        # In Cloudflare Python workers, js Response headers might need iteration
        # but for httpx we can just return a basic mapping

        return httpx.Response(
            status_code=res.status,
            headers=res_headers,
            content=content,
            request=request,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Mocks for demonstration if the user types 'demo'
# ─────────────────────────────────────────────────────────────────────────────

MOCK_LIST = {
  "data": [
    {
      "conversation_id": "c_12345",
      "status": "active",
      "created_at": "2024-03-01T12:00:00Z"
    },
    {
      "conversation_id": "c_67890",
      "status": "completed",
      "created_at": "2024-03-01T10:00:00Z"
    }
  ],
  "total_count": 2
}

MOCK_GET = {
  "conversation_id": "c_12345",
  "status": "active",
  "created_at": "2024-03-01T12:00:00Z",
  "duration_seconds": 120,
  "metadata": {"user": "demo-user"}
}

# ─────────────────────────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────────────────────────

async def handle_info():
    try:
        import importlib.metadata
        version = importlib.metadata.version("astrocyte-integration-tavus")
    except Exception:
        version = "unknown"
    return json_response({"version": version})


async def handle_list(request, qs: dict):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return json_response({"error": "Missing or invalid Authorization header"}, status=401)

    api_key = auth[7:]

    if api_key.lower() == "demo":
        return json_response({"result": MOCK_LIST})

    if api_key == "needs_api_key":
        return json_response({"error": "Needs API Key to proceed with this request."}, status=400)

    try:
        # Use our custom transport to fetch via js_fetch instead of sockets
        client = httpx.AsyncClient(transport=FetchAsyncTransport(), base_url="https://tavusapi.com/v2")

        # Instantiate the real client, passing our custom httpx client
        tavus = TavusClient(api_key=api_key, client=client)

        limit = qs.get("limit")
        limit = int(limit) if limit and limit.isdigit() else None
        status = qs.get("status")
        page = qs.get("page")
        page = int(page) if page and page.isdigit() else None

        # We call the real library's list_conversations method
        # which will use our transport and make a real request
        data = await tavus.list_conversations(limit=limit, page=page, status=status)
        return json_response({"result": data})

    except TavusAPIError as e:
        return json_response({"error": f"Tavus API Error: {str(e)}"}, status=e.status_code)
    except Exception as e:
        return json_response({"error": f"Internal Error: {str(e)}"}, status=500)


async def handle_get(request, qs: dict):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return json_response({"error": "Missing or invalid Authorization header"}, status=401)

    api_key = auth[7:]
    conv_id = qs.get("conversation_id")
    if not conv_id:
        return json_response({"error": "Missing conversation_id"}, status=400)

    if api_key.lower() == "demo":
        return json_response({"result": MOCK_GET})

    if api_key == "needs_api_key":
        return json_response({"error": "Needs API Key to proceed with this request."}, status=400)

    try:
        # Use our custom transport to fetch via js_fetch instead of sockets
        client = httpx.AsyncClient(transport=FetchAsyncTransport(), base_url="https://tavusapi.com/v2")

        # Instantiate the real client, passing our custom httpx client
        tavus = TavusClient(api_key=api_key, client=client)

        data = await tavus.get_conversation(conv_id)
        return json_response({"result": data})

    except TavusAPIError as e:
        return json_response({"error": f"Tavus API Error: {str(e)}"}, status=e.status_code)
    except Exception as e:
        return json_response({"error": f"Internal Error: {str(e)}"}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url  = str(request.url)
    qs   = parse_qs(url)
    path = url.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()
    elif path == "/api/list_conversations":
        return await handle_list(request, qs)
    elif path == "/api/get_conversation":
        return await handle_get(request, qs)
    else:
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)
