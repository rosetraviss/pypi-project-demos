import json
from js import Response, Headers
from pyodide.ffi import to_js
from pyodide.http import pyfetch

import atendeaqui
from atendeaqui.client import AtendeAquiClient
from atendeaqui._http import HttpClient
from atendeaqui.exceptions import ERROR_CODE_MAP, AtendeAquiError

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AtendeAqui SDK Demo | Cloudflare Python Worker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <style>
    :root {
      --bg: #0f172a; --surface: #1e293b; --surface-hover: #334155;
      --text: #f8fafc; --muted: #94a3b8; --border: #334155;
      --primary: #3b82f6; --primary-hover: #2563eb;
      --success: #10b981; --error: #ef4444;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg); color: var(--text);
      font-family: var(--font); min-height: 100vh;
      display: flex; flex-direction: column;
      line-height: 1.5;
    }
    header {
      background: var(--surface); border-bottom: 1px solid var(--border);
      padding: 1.5rem 2rem; text-align: center;
    }
    header h1 { font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; }
    header p { color: var(--muted); font-size: 0.875rem; margin-top: 0.5rem; }
    main {
      flex: 1; max-width: 800px; width: 100%; margin: 2rem auto;
      padding: 0 1rem; display: flex; flex-direction: column; gap: 1.5rem;
    }
    .panel {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .panel h2 { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
    .form-group { margin-bottom: 1rem; }
    .form-group label { display: block; font-size: 0.875rem; color: var(--muted); margin-bottom: 0.25rem; }
    .form-group input {
      width: 100%; padding: 0.75rem; border-radius: 6px;
      border: 1px solid var(--border); background: var(--bg); color: var(--text);
      font-family: inherit; font-size: 1rem; transition: border-color 0.2s;
    }
    .form-group input:focus { outline: none; border-color: var(--primary); }
    button {
      background: var(--primary); color: white; border: none;
      padding: 0.75rem 1.5rem; border-radius: 6px; font-size: 1rem;
      font-weight: 500; cursor: pointer; transition: background-color 0.2s, transform 0.1s;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    }
    button:hover { background: var(--primary-hover); }
    button:active { transform: scale(0.98); }
    button:disabled { background: var(--muted); cursor: not-allowed; opacity: 0.7; }
    .spinner {
      width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%; border-top-color: white; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .result-box {
      margin-top: 1.5rem; padding: 1rem; border-radius: 6px;
      background: var(--bg); border: 1px solid var(--border);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.875rem; white-space: pre-wrap; word-break: break-all;
      display: none;
    }
    .result-box.show { display: block; animation: fadeIn 0.3s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
    .status-success { border-left: 4px solid var(--success); }
    .status-error { border-left: 4px solid var(--error); }
    footer {
      text-align: center; padding: 1.5rem; border-top: 1px solid var(--border);
      color: var(--muted); font-size: 0.875rem; background: var(--surface);
    }
    footer a { color: var(--primary); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <h1>AtendeAqui Python SDK Demo</h1>
    <p>Running natively in a Cloudflare Worker via Pyodide</p>
  </header>

  <main>
    <div class="panel">
      <h2>Simulate Onboarding Start</h2>
      <p style="margin-bottom: 1rem; color: var(--muted); font-size: 0.9rem;">
        This demo overrides the internal HTTP client of <code>atendeaqui</code> to use Cloudflare's async fetch. Enter details below to simulate starting an onboarding flow.
      </p>

      <div class="form-group">
        <label for="flow-key">Flow Key (UUID)</label>
        <input type="text" id="flow-key" value="demo-flow-1234" placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000">
      </div>
      <div class="form-group">
        <label for="user-id">User ID</label>
        <input type="text" id="user-id" value="user_789" placeholder="External User ID">
      </div>
      <div class="form-group">
        <label for="user-name">Name (optional)</label>
        <input type="text" id="user-name" value="Jane Doe" placeholder="User Name">
      </div>

      <button id="start-btn" onclick="startFlow()">Start Flow</button>

      <div id="result" class="result-box"></div>
    </div>
  </main>

  <footer>
    <p>Package Demo for <a href="https://pypi.rosetraviss.uk/atendeaqui" target="_blank">atendeaqui 1.0.1</a></p>
    <p>Hosted by <a href="https://pypi.rosetraviss.uk" target="_blank">PyPI Mirror</a></p>
  </footer>

  <script>
    async function startFlow() {
      const btn = document.getElementById('start-btn');
      const res = document.getElementById('result');

      const flowKey = document.getElementById('flow-key').value;
      const userId = document.getElementById('user-id').value;
      const userName = document.getElementById('user-name').value;

      if (!flowKey || !userId) {
        res.textContent = "Error: Flow Key and User ID are required.";
        res.className = "result-box show status-error";
        return;
      }

      btn.disabled = true;
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="spinner"></div> Processing...';

      try {
        const response = await fetch('/api/start-flow', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ flow_key: flowKey, user_id: userId, name: userName })
        });

        const data = await response.json();
        res.textContent = JSON.stringify(data, null, 2);

        if (response.ok) {
          res.className = "result-box show status-success";
        } else {
          res.className = "result-box show status-error";
        }
      } catch (error) {
        res.textContent = "Network Error: " + error.message;
        res.className = "result-box show status-error";
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  </script>
</body>
</html>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#3b82f6" />
  <path d="M30 50 L45 65 L70 35" fill="none" stroke="white" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
</svg>"""

LLMS_TXT = """# AtendeAqui Cloudflare Worker Demo

This repository contains a demo for the `atendeaqui` Python package, running inside a Cloudflare Python Worker via Pyodide.

Since Cloudflare Workers do not support synchronous socket-based requests (used by the `requests` library), this demo intercepts the SDK's internal `HttpClient` and mocks the responses to showcase the API without actual network calls.

The worker serves an HTML interface to interact with the mocked API.
"""

# ==============================================================================
# Async Mock HTTP Client for AtendeAqui SDK
# ==============================================================================
# In a real environment, we would use pyfetch, but since we don't have a real
# backend for the demo and 'requests' isn't supported, we mock the responses.
# ==============================================================================

class AsyncMockHttpClient(HttpClient):
    """
    Mocked HTTP client that overrides the synchronous methods of atendeaqui.HttpClient
    to return synthetic responses or simulate API calls.
    """
    def __init__(self, base_url: str, headers: dict, timeout: int = 30):
        # We don't call super() to avoid creating requests.Session()
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout
        self.headers = headers

    def get(self, path: str, params: dict | None = None, headers: dict | None = None) -> dict:
        raise NotImplementedError("Async mock get not implemented")

    def post(self, path: str, json: dict | None = None, headers: dict | None = None) -> dict:
        # Simulate /v1/onboarding/flows/{flow_key}/start
        if "onboarding/flows" in path and path.endswith("/start"):
            flow_key = path.split("/")[-2]
            return {
                "external_user_id": json.get("user_id"),
                "external_user_name": json.get("name"),
                "external_user_email": None,
                "flow_name": "Demo Flow",
                "flow_slug": "demo-flow",
                "status": "IN_PROGRESS",
                "current_step_key": "welcome",
                "current_step_title": "Welcome to AtendeAqui",
                "completion_percentage": 0,
                "steps_completed": [],
                "steps_skipped": [],
                "step_data": {},
                "client_id": None,
                "started_at": "2024-06-07T18:00:00Z",
                "completed_at": None,
                "last_activity_at": "2024-06-07T18:00:00Z"
            }

        return {"mocked": True, "path": path}

    def patch(self, path: str, json: dict | None = None, headers: dict | None = None) -> dict:
        raise NotImplementedError("Async mock patch not implemented")

    def put(self, path: str, json: dict | None = None, headers: dict | None = None) -> dict:
        raise NotImplementedError("Async mock put not implemented")

    def delete(self, path: str, headers: dict | None = None) -> dict:
        raise NotImplementedError("Async mock delete not implemented")


# Patch the HTTP client in the library
atendeaqui.client.HttpClient = AsyncMockHttpClient


# ==============================================================================
# API Helpers
# ==============================================================================

def json_response(data, status=200):
    headers = Headers.new([
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
        ("Cache-Control", "no-cache"),
    ])
    return Response.new(json.dumps(data), headers=headers, status=status)

async def handle_start_flow(request):
    try:
        req_json = await request.json()
        req_dict = req_json.to_py()
    except Exception:
        return json_response({"error": "Invalid JSON"}, status=400)

    flow_key = req_dict.get("flow_key")
    user_id = req_dict.get("user_id")
    name = req_dict.get("name")

    if not flow_key or not user_id:
        return json_response({"error": "flow_key and user_id are required"}, status=400)

    try:
        # Initialize client with sandbox=True
        client = AtendeAquiClient(flow_key=flow_key, sandbox=True)

        # Call the SDK method
        progress = client.onboarding.start_flow(
            user_id=user_id,
            flow_key=flow_key,
            name=name
        )

        # Serialize the dataclass
        import dataclasses
        return json_response({
            "status": "success",
            "message": "Flow started successfully (mocked)",
            "data": dataclasses.asdict(progress)
        })

    except Exception as e:
        return json_response({"error": str(e), "type": type(e).__name__}, status=500)


# ==============================================================================
# Entry point
# ==============================================================================

async def on_fetch(request, env):
    url = str(request.url)
    path = url.split("?")[0]

    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new([
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*")
        ])
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new([
            ("Content-Type", "image/svg+xml"),
            ("Cache-Control", "public, max-age=86400")
        ])
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/start-flow" and request.method == "POST":
        return await handle_start_flow(request)

    # Default route: Serve HTML
    headers = Headers.new([("Content-Type", "text/html; charset=utf-8")])
    return Response.new(HTML, headers=headers)
