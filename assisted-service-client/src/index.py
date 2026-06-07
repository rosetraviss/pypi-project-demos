"""
assisted-service-client Demo — Cloudflare Python Worker
"""

import json
import assisted_service_client
from assisted_service_client import Configuration, ApiClient

from js import Response, Headers

LLMS_TXT = """# assisted-service-client Cloudflare Worker Demo
This is a demo of `assisted-service-client` running as a Cloudflare Python Worker.
See https://pypi.rosetraviss.uk/assisted-service-client
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🤖</text></svg>"""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>assisted-service-client Demo · Cloudflare Python Worker</title>
  <style>
    :root {
      --bg: #0f172a; --surface: #1e293b; --text: #f8fafc; --accent: #38bdf8;
      --muted: #94a3b8; --border: #334155;
    }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.6; margin: 0; padding: 2rem;
    }
    .container { max-width: 800px; margin: 0 auto; }
    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 2rem; margin-top: 2rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-2px); }
    h1 { color: var(--accent); margin-top: 0; }
    button {
      background: var(--accent); color: var(--bg);
      border: none; padding: 0.75rem 1.5rem;
      border-radius: 6px; font-weight: bold; cursor: pointer;
      transition: opacity 0.2s;
    }
    button:hover { opacity: 0.9; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    pre {
      background: var(--bg); padding: 1rem;
      border-radius: 6px; overflow-x: auto;
      border: 1px solid var(--border);
    }
    .footer {
      margin-top: 4rem; text-align: center; color: var(--muted);
      font-size: 0.875rem;
      padding-top: 2rem; border-top: 1px solid var(--border);
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .spinner {
      display: inline-block; width: 1rem; height: 1rem;
      border: 2px solid var(--bg); border-top-color: transparent;
      border-radius: 50%; animation: spin 1s linear infinite;
      vertical-align: middle; margin-right: 0.5rem;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="container">
    <h1>assisted-service-client</h1>
    <p>Live Pyodide demo of the OpenShift Assisted Installer client library.</p>

    <div class="card">
      <h2>Client Configuration</h2>
      <p>Click below to initialize the client configuration and inspect its default properties.</p>
      <button id="inspectBtn" onclick="inspectConfig()">Inspect Configuration</button>
      <div id="result" style="display:none; margin-top: 1.5rem;">
        <h3>Configuration Output</h3>
        <pre><code id="outputCode"></code></pre>
      </div>
    </div>

    <div class="footer">
      Demo for <a href="https://pypi.rosetraviss.uk/assisted-service-client">assisted-service-client</a> |
      <a href="https://pypi.rosetraviss.uk">pypi.rosetraviss.uk</a>
    </div>
  </div>

  <script>
    async function inspectConfig() {
      const btn = document.getElementById('inspectBtn');
      const result = document.getElementById('result');
      const out = document.getElementById('outputCode');

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>Loading...';

      try {
        const res = await fetch('/api/inspect');
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
        result.style.display = 'block';
      } catch (err) {
        out.textContent = 'Error: ' + err.message;
        result.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Inspect Configuration';
      }
    }
  </script>
</body>
</html>"""

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

async def handle_info():
    try:
        symbols = dir(assisted_service_client)
        public_symbols = [s for s in symbols if not s.startswith("_")]

        return json_response({
            "status": "ok",
            "package": "assisted-service-client",
            "symbol_count": len(public_symbols),
            "sample_symbols": public_symbols[:10]
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def handle_inspect():
    try:
        config = Configuration()

        data = {
            "default_host": config.host,
            "api_key_prefix": config.api_key_prefix,
            "verify_ssl": config.verify_ssl,
            "ssl_ca_cert": config.ssl_ca_cert,
            "cert_file": config.cert_file,
            "key_file": config.key_file,
            "debug": config.debug,
            "logger_format": config.logger_format,
            "temp_folder_path": config.temp_folder_path
        }

        return json_response(data)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def on_fetch(request, env):
    url = str(request.url)
    path = url.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        # Use LLMS_TXT for both for simplicity as they are essentially placeholders
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()
    elif path == "/api/inspect":
        return await handle_inspect()
    else:
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)
