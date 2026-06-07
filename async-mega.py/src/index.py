import sys
import json
from unittest.mock import MagicMock

# Mock Crypto packages to avoid native compilation issues in Pyodide
class DummyModule:
    pass

for mod in [
    'Crypto', 'Crypto.Cipher', 'Crypto.Cipher.AES',
    'Crypto.PublicKey', 'Crypto.PublicKey.RSA',
    'Crypto.Util', 'Crypto.Util.Counter',
    'Crypto.Math', 'Crypto.Math.Numbers',
    'Crypto.Hash', 'Crypto.Hash.SHA256',
    'Crypto.Random',
]:
    sys.modules[mod] = MagicMock()

from js import Response, Headers

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">☁️</text></svg>"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>async-mega.py Demo</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; background: #f9fafb; color: #111827; margin: 0; display: flex; flex-direction: column; min-height: 100vh; }
    header { background: #1e3a8a; color: white; padding: 1rem 2rem; }
    main { flex: 1; max-width: 800px; margin: 2rem auto; padding: 0 1rem; width: 100%; }
    .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 2rem; margin-bottom: 2rem; transition: transform 0.2s; }
    .card:hover { transform: translateY(-2px); }
    button { background: #2563eb; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; transition: background 0.2s; }
    button:hover { background: #1d4ed8; }
    #result { margin-top: 1rem; padding: 1rem; background: #f3f4f6; border-radius: 4px; display: none; }
    footer { text-align: center; padding: 2rem; background: #e5e7eb; color: #4b5563; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <h1>async-mega.py Demo</h1>
  </header>
  <main>
    <div class="card">
      <h2>Check Package Status</h2>
      <p>Click below to initialize the async-mega.py client (mocked crypto for this demo).</p>
      <button onclick="checkStatus()">Check Status</button>
      <div id="result"></div>
    </div>
  </main>
  <footer>
    <p>Return to <a href="https://pypi.rosetraviss.uk">Rose's PyPI Mirror</a> | <a href="https://pypi.org/project/async-mega-py/">async-mega-py on PyPI</a></p>
  </footer>
  <script>
    async function checkStatus() {
      const resEl = document.getElementById('result');
      resEl.style.display = 'block';
      resEl.textContent = 'Checking...';
      try {
        const r = await fetch('/api/status');
        const data = await r.json();
        resEl.textContent = data.message;
      } catch (e) {
        resEl.textContent = 'Error: ' + e.message;
      }
    }
  </script>
</body>
</html>
"""

async def on_fetch(request, env):
    url = str(request.url)
    path = "/" + url.split("/", 3)[-1] if "://" in url else url.split("?")[0]

    if path == "/api/status":
        headers = Headers.new({"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}.items())
        try:
            import mega
            from mega.client import MegaNzClient
            return Response.new(json.dumps({"status": "ok", "message": "Successfully imported async-mega.py client!"}), headers=headers)
        except Exception as e:
            return Response.new(json.dumps({"status": "error", "message": str(e)}), headers=headers, status=500)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
