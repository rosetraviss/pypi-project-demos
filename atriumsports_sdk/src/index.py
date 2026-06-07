"""
AtriumSports SDK Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/atriumsports_sdk/

We mock pydantic_core and requests to bypass Pyodide limitations.
"""

import sys
import json
from types import ModuleType

# ─────────────────────────────────────────────────────────────────────────────
# Pyodide Workarounds
# ─────────────────────────────────────────────────────────────────────────────

# 1. Mock pydantic_core (C extension, unsupported in Pyodide)
class MockCoreSchema:
    pass

class MockSchemaValidator:
    def __init__(self, *args, **kwargs):
        pass
    def validate_python(self, *args, **kwargs):
        return args[0] if args else None
    def validate_json(self, *args, **kwargs):
        return args[0] if args else None
    def validate_assignment(self, *args, **kwargs):
        return args[0] if args else None

class MockPydanticUndefinedType:
    pass

PydanticUndefined = MockPydanticUndefinedType()

class MockValidationError(Exception):
    def __init__(self, title, errors):
        super().__init__(f"{title}: {errors}")
        self.title = title
        self.errors = errors

mock_pydantic_core = ModuleType("pydantic_core")
mock_pydantic_core.__version__ = "2.46.4"
mock_pydantic_core.PydanticUndefined = PydanticUndefined
mock_pydantic_core.PydanticUndefinedType = MockPydanticUndefinedType
mock_pydantic_core.core_schema = MockCoreSchema()
mock_pydantic_core.CoreSchema = MockCoreSchema
mock_pydantic_core.SchemaValidator = MockSchemaValidator
mock_pydantic_core.ValidationError = MockValidationError

sys.modules["pydantic_core"] = mock_pydantic_core
sys.modules["pydantic_core._pydantic_core"] = mock_pydantic_core

# 2. Mock requests and urllib3 (socket limitations)
# We don't actually need to mock the full requests since we'll intercept at the worker level if needed,
# but for safety let's mock requests so it doesn't try to use native sockets if AtriumSports init calls it.
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
        self.text = json.dumps(json_data)
    def json(self):
        return self._json_data
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}")

def mock_request(*args, **kwargs):
    # Just return a fake successful response to bypass initial checks if any
    return MockResponse(200, {"token": "fake-token"})

mock_requests = ModuleType("requests")
mock_requests.get = mock_request
mock_requests.post = mock_request
mock_requests.put = mock_request
mock_requests.delete = mock_request
mock_requests.exceptions = ModuleType("exceptions")
mock_requests.exceptions.RequestException = Exception

sys.modules["requests"] = mock_requests

# Also mock paho-mqtt just in case it attempts to initialize threads or sockets
class MockMQTT:
    class Client:
        def __init__(self, *args, **kwargs): pass
        def connect(self, *args, **kwargs): pass
        def loop_start(self): pass
        def loop_stop(self): pass
        def subscribe(self, *args, **kwargs): pass
mock_mqtt = ModuleType("paho.mqtt.client")
mock_mqtt.Client = MockMQTT.Client
mock_mqtt.error_string = lambda *args, **kwargs: ""
sys.modules["paho"] = ModuleType("paho")
sys.modules["paho.mqtt"] = ModuleType("paho.mqtt")
sys.modules["paho.mqtt.client"] = mock_mqtt


# ── Real Package Imports ──────────────────────────────────────────────────────
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python_modules"))

try:
    from atriumsports import AtriumSports
except ImportError as e:
    AtriumSports = None
    import_error = str(e)


# ── Workers JS FFI ────────────────────────────────────────────────────────────
from js import Response, Headers, fetch as js_fetch


# ─────────────────────────────────────────────────────────────────────────────
# Assets & Docs
# ─────────────────────────────────────────────────────────────────────────────

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🏀</text></svg>"""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>atriumsports_sdk Demo · Cloudflare Python Worker</title>
  <meta name="description" content="Live demo of the atriumsports_sdk PyPI package running as a Cloudflare Python Worker.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    /* Modern Technical Theme */
    :root {
      --surface: #f7f9ff;
      --surface-dim: #bddeff;
      --surface-container-low: #edf4ff;
      --surface-container: #e2efff;
      --on-surface: #001d32;
      --on-surface-variant: #41474f;
      --primary: #145d91;
      --on-primary: #ffffff;
      --primary-container: #3776ab;
      --on-primary-container: #f5f8ff;
      --secondary: #725c00;
      --secondary-container: #fed33a;
      --on-secondary-container: #715b00;
      --tertiary: #316600;
      --error: #ba1a1a;
      --outline: #717880;
      --background: #f7f9ff;

      --rounded: 4px;
      --rounded-lg: 8px;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: var(--background); color: var(--on-surface); min-height: 100vh; display: flex; flex-direction: column; }

    .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; flex: 1; }

    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 48px; border-bottom: 1px solid var(--outline); padding-bottom: 16px; }
    .title { font-size: 28px; font-weight: 600; color: var(--primary); letter-spacing: -0.01em; }
    .badge-container { display: flex; gap: 8px; }
    .badge { padding: 4px 8px; border-radius: var(--rounded); font-size: 12px; font-weight: 600; text-decoration: none; font-family: 'JetBrains Mono', monospace; }
    .badge-primary { background: var(--primary-container); color: var(--on-primary-container); }
    .badge-secondary { background: var(--surface-container); color: var(--primary); border: 1px solid var(--primary); }

    .hero { margin-bottom: 48px; }
    .hero h1 { font-size: 36px; font-weight: 700; margin-bottom: 16px; letter-spacing: -0.02em; }
    .hero p { font-size: 18px; color: var(--on-surface-variant); line-height: 28px; max-width: 800px; }

    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 24px; margin-bottom: 48px; }

    .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: var(--rounded-lg); padding: 24px; box-shadow: 0 1px 3px rgba(31,66,94,0.05); transition: box-shadow 0.2s; }
    .card:hover { box-shadow: 0 4px 12px rgba(31,66,94,0.08); }
    .card-title { font-size: 20px; font-weight: 600; margin-bottom: 16px; color: var(--primary); }
    .card p { font-size: 14px; color: var(--on-surface-variant); line-height: 20px; margin-bottom: 16px; }

    .code-block { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: var(--rounded-lg); padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #1e293b; overflow-x: auto; white-space: pre; line-height: 22px; }
    .code-block .kw { color: #005cc5; }
    .code-block .str { color: #032f62; }
    .code-block .cmt { color: #6a737d; }

    .demo-section { background: #ffffff; border: 1px solid #e2e8f0; border-radius: var(--rounded-lg); padding: 24px; margin-bottom: 48px; }
    .demo-header { margin-bottom: 24px; }

    button { background: var(--primary); color: #fff; border: none; padding: 12px 24px; border-radius: var(--rounded); font-weight: 600; cursor: pointer; transition: background 0.2s; font-family: 'Inter', sans-serif; }
    button:hover { background: #0f4b75; }
    button:disabled { background: var(--outline); cursor: not-allowed; }

    .result-box { margin-top: 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: var(--rounded-lg); padding: 16px; min-height: 100px; font-family: 'JetBrains Mono', monospace; font-size: 14px; white-space: pre-wrap; word-break: break-all; }

    .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 8px; }
    @keyframes spin { to { transform: rotate(360deg); } }

    footer { padding: 32px 24px; text-align: center; border-top: 1px solid var(--outline); color: var(--on-surface-variant); font-size: 14px; background: #ffffff; }
    footer a { color: var(--primary); text-decoration: none; font-weight: 600; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="title">atriumsports_sdk</div>
      <div class="badge-container">
        <span class="badge badge-primary">Pyodide Environment</span>
        <a href="https://pypi.rosetraviss.uk/atriumsports_sdk" target="_blank" class="badge badge-secondary">pip install atriumsports_sdk</a>
      </div>
    </header>

    <div class="hero">
      <h1>AtriumSports SDK in Cloudflare Workers</h1>
      <p>Demonstrating the <code>atriumsports_sdk</code> library. This demo mocks network sockets and C-extensions (like <code>pydantic_core</code>) to run gracefully inside the Pyodide WebAssembly runtime.</p>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-title">Package Instantiation</div>
        <p>Creating an AtriumSports client instance configures access to the Datacore API.</p>
        <div class="code-block"><span class="kw">from</span> atriumsports <span class="kw">import</span> AtriumSports

client = AtriumSports({
    <span class="str">"sport"</span>: <span class="str">"basketball"</span>,
    <span class="str">"credential_id"</span>: <span class="str">"API_KEY"</span>,
    <span class="str">"credential_secret"</span>: <span class="str">"API_SECRET"</span>,
    <span class="str">"organizations"</span>: [<span class="str">"org-123"</span>],
    <span class="str">"environment"</span>: <span class="str">"production"</span>
})</div>
      </div>

      <div class="card">
        <div class="card-title">Datacore Usage</div>
        <p>Access the Datacore API using the client instance.</p>
        <div class="code-block"><span class="cmt"># Get a Datacore API client</span>
datacore = client.client(<span class="str">"datacore"</span>)

<span class="kw">with</span> datacore <span class="kw">as</span> api:
    <span class="cmt"># Perform operations</span>
    <span class="cmt"># competitions = CompetitionsApi(api)</span>
    <span class="kw">pass</span></div>
      </div>
    </div>

    <div class="demo-section">
      <div class="demo-header">
        <h2 style="font-size: 24px; color: var(--primary); margin-bottom: 8px;">Interactive Demo</h2>
        <p style="color: var(--on-surface-variant);">Enter your API credentials below to instantiate the SDK class within this Pyodide worker.</p>
      </div>

      <div style="display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px;">
          <label for="cred-id" style="display: block; font-size: 14px; font-weight: 600; margin-bottom: 8px;">Credential ID (API Key)</label>
          <input type="text" id="cred-id" placeholder="e.g. key_12345" style="width: 100%; padding: 10px; border: 1px solid var(--outline); border-radius: var(--rounded); font-family: 'JetBrains Mono', monospace; font-size: 14px; outline: none;">
        </div>
        <div style="flex: 1; min-width: 250px;">
          <label for="cred-secret" style="display: block; font-size: 14px; font-weight: 600; margin-bottom: 8px;">Credential Secret</label>
          <input type="password" id="cred-secret" placeholder="••••••••••••" style="width: 100%; padding: 10px; border: 1px solid var(--outline); border-radius: var(--rounded); font-family: 'JetBrains Mono', monospace; font-size: 14px; outline: none;">
        </div>
      </div>

      <button id="run-btn" onclick="runDemo()">Instantiate SDK</button>
      <div id="result" class="result-box">Ready.</div>
    </div>
  </div>

  <footer>
    <p>
      Demo running on <a href="https://developers.cloudflare.com/workers/languages/python/" target="_blank">Cloudflare Python Workers</a> (Pyodide) ·
      Library: <a href="https://pypi.rosetraviss.uk/atriumsports_sdk" target="_blank">atriumsports_sdk</a> ·
      Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
    </p>
  </footer>

  <script>
    async function runDemo() {
      const btn = document.getElementById('run-btn');
      const res = document.getElementById('result');
      const credId = document.getElementById('cred-id').value.trim() || 'DEMO_ID';
      const credSecret = document.getElementById('cred-secret').value.trim() || 'DEMO_SECRET';

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Running...';
      res.style.color = 'var(--on-surface)';
      res.textContent = 'Initializing...';

      try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential_id: credId, credential_secret: credSecret })
        });
        const data = await response.json();

        if (data.error) {
          res.style.color = 'var(--error)';
          res.textContent = `Error: ${data.error}`;
        } else {
          res.textContent = JSON.stringify(data.result, null, 2);
        }
      } catch (err) {
        res.style.color = 'var(--error)';
        res.textContent = `Fetch error: ${err.message}`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Instantiate SDK';
      }
    }
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# API Handlers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new([
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
    ])
    return Response.new(json.dumps(data), headers=headers, status=status)

async def handle_run(request):
    if AtriumSports is None:
        return json_response({"error": f"Failed to import atriumsports. Error: {globals().get('import_error')}"}, status=500)

    try:
        if request.method == "POST":
            try:
                # the result of await request.json() in Pyodide is often a JsProxy dictionary-like object
                # We need to convert it to a normal python dict or get its attributes appropriately
                body_proxy = await request.json()
                try:
                    cred_id = body_proxy.credential_id
                except AttributeError:
                    cred_id = body_proxy.get("credential_id", "DEMO_ID") if hasattr(body_proxy, 'get') else "DEMO_ID"

                try:
                    cred_secret = body_proxy.credential_secret
                except AttributeError:
                    cred_secret = body_proxy.get("credential_secret", "DEMO_SECRET") if hasattr(body_proxy, 'get') else "DEMO_SECRET"

            except Exception as ex:
                cred_id = "DEMO_ID"
                cred_secret = f"DEMO_SECRET ({str(ex)})"
        else:
            cred_id = "DEMO_ID"
            cred_secret = "DEMO_SECRET"

        # Instantiate the SDK
        client = AtriumSports({
            "sport": "basketball",
            "credential_id": cred_id,
            "credential_secret": cred_secret,
            "organizations": ["demo-org"],
            "environment": "production"
        })

        datacore = client.client("datacore")

        # We can't actually make network calls to atrium without real credentials and proper pyfetch mappings
        # But we can prove the class instantiates and returns the configured datacore client

        return json_response({
            "result": {
                "status": "Success",
                "message": "AtriumSports SDK instantiated successfully inside Pyodide worker.",
                "client_options": client._options,
                "datacore_client_type": str(type(datacore).__name__)
            }
        })

    except Exception as e:
        import traceback
        return json_response({"error": str(e), "trace": traceback.format_exc()}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# Fetch Event Router
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url = str(request.url)
    path = "/" + url.split("://", 1)[1].split("/", 1)[-1].split("?")[0] if "://" in url else url.split("?")[0]

    if path == "/":
        headers = Headers.new([("Content-Type", "text/html; charset=utf-8")])
        return Response.new(HTML, headers=headers)

    if path == "/api/run":
        return await handle_run(request)

    if path == "/favicon.ico":
        headers = Headers.new([("Content-Type", "image/svg+xml"), ("Cache-Control", "public, max-age=86400")])
        return Response.new(FAVICON_SVG, headers=headers)

    return Response.new("Not Found", status=404)
