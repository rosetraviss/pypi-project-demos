import json
from js import Response, Headers

try:
    import assinafy
    from assinafy import AssinafyClient
    # Instantiate without networking actually failing on init
    client = AssinafyClient(api_key="demo")
    SDK_VERSION = getattr(assinafy, "__version__", "unknown")

    # Collect initialized resources
    RESOURCES = []
    for res in ["authentication", "documents", "signers", "signer_documents", "assignments", "webhooks", "templates", "tags", "fields"]:
        if hasattr(client, res):
            RESOURCES.append(res)
except Exception as e:
    SDK_VERSION = "unknown"
    RESOURCES = [f"Error: {str(e)}"]

# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

LLMS_TXT = """# assinafy Demo API

> Live demo API and UI for the `assinafy` package on Cloudflare Workers, providing an interface to verify SDK capabilities.

## Deployment Details
- **Demo URL**: https://assinafy.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/assinafy
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoint

### `GET /api/info`
Returns general metadata confirming the package functionality in the Cloudflare Python Worker environment.

#### Response Body
- `version` (string): The current SDK version initialized.
- `client_resources` (array of strings): A list of API resources instantiated properly on the AssinafyClient object.
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#3b82f6"/>
  <path d="M30 70 L50 30 L70 70 Z" fill="#ffffff"/>
</svg>"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>assinafy SDK Demo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/svg+xml" href="/favicon.ico">
  <style>
    :root {
      --bg: #0f172a; --panel: #1e293b; --text: #f8fafc;
      --accent: #3b82f6; --accent-hover: #2563eb;
      --border: #334155; --muted: #94a3b8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 2rem;
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg); color: var(--text);
      display: flex; flex-direction: column; align-items: center;
      min-height: 100vh;
    }
    header { text-align: center; margin-bottom: 2rem; }
    h1 { margin: 0 0 0.5rem; font-size: 2.5rem; letter-spacing: -0.02em; }
    h1 span { color: var(--accent); }
    .subtitle { color: var(--muted); font-size: 1.1rem; }

    main {
      width: 100%; max-width: 600px;
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 12px; padding: 2rem;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    main:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.2);
    }

    .status-card {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.2);
      border-radius: 8px; padding: 1.5rem;
      margin-bottom: 1.5rem;
      text-align: center;
    }
    .status-card h2 { margin: 0 0 0.5rem; font-size: 1.2rem; }
    .status-value { font-family: monospace; font-size: 1.1rem; color: #60a5fa; }

    .resources-list {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 0.75rem; margin-top: 1rem;
    }
    .resource-tag {
      background: #334155; padding: 0.5rem 0.75rem; border-radius: 6px;
      font-size: 0.9rem; text-align: center; color: #cbd5e1;
      border: 1px solid #475569;
      transition: all 0.2s;
    }
    .resource-tag:hover {
      background: var(--accent); border-color: var(--accent); color: white;
    }

    footer {
      margin-top: auto; padding-top: 3rem;
      text-align: center; color: var(--muted); font-size: 0.9rem;
    }
    footer a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
    footer a:hover { color: var(--accent-hover); text-decoration: underline; }

    .spinner {
      display: inline-block; width: 1.5rem; height: 1.5rem;
      border: 3px solid rgba(255,255,255,0.3); border-radius: 50%;
      border-top-color: var(--text); animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <header>
    <h1><span>assinafy</span> Demo</h1>
    <div class="subtitle">Cloudflare Python Worker</div>
  </header>

  <main id="content">
    <div style="text-align:center"><div class="spinner"></div></div>
  </main>

  <footer>
    &copy; 2024 <a href="https://pypi.rosetraviss.uk" target="_blank">PyPI Mirror</a> &bull;
    <a href="/api/info">/api/info</a> &bull;
    <a href="/llms.txt">llms.txt</a>
  </footer>

  <script>
    async function init() {
      const content = document.getElementById('content');
      try {
        const r = await fetch('/api/info');
        const d = await r.json();

        let tagsHtml = d.client_resources.map(res => `<div class="resource-tag">${res}</div>`).join('');

        content.innerHTML = `
          <div class="status-card">
            <h2>SDK Version</h2>
            <div class="status-value">${d.version}</div>
          </div>
          <h2 style="font-size: 1.1rem; margin-bottom: 0.5rem;">Loaded Client Resources:</h2>
          <div class="resources-list">
            ${tagsHtml}
          </div>
        `;
      } catch (e) {
        content.innerHTML = `<div style="color: #ef4444; text-align: center;">Error loading API: ${e.message}</div>`;
      }
    }
    init();
  </script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# API handlers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-store",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

async def handle_info():
    return json_response({
        "version": SDK_VERSION,
        "client_resources": RESOURCES
    })

# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url = str(request.url)
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
    else:
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)
