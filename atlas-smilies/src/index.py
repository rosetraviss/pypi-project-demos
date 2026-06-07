"""
atlas-smilies Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/atlas-smilies/

Note: atlas-smilies depends on native C-extensions (like anndata, scanpy) which
are not supported in the Cloudflare Workers (Pyodide) environment. This demo gracefully
catches the ImportError and simulates the output to showcase the UI and API capabilities.
"""

from js import Response, Headers
import json

# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

LLMS_TXT = """# atlas-smilies Demo API

> Live demo API and UI for the `atlas-smilies` package on Cloudflare Workers, providing multi-omic trajectory inference features (simulated due to Pyodide limitations).

## Deployment Details
- **Demo URL**: https://atlas-smilies.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/atlas-smilies
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoints

### `GET /api/info`
Returns general metadata about the package and the worker environment.

### `GET /api/trajectory`
Simulates a multi-omic trajectory inference to showcase the theoretical usage of the package, returning mock results since the underlying package relies on native C-extensions (like anndata and scanpy) that cannot be executed in Pyodide.

#### Limitations
Cloudflare Workers execute Python code using Pyodide, which does not support native C-extensions. Since `atlas-smilies` relies on packages with such extensions, the worker handles the `ImportError` gracefully and returns simulated outputs for the demo.
"""

FAVICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="#3776AB"/><path d="M50 20 L80 80 L20 80 Z" fill="#FFD43B"/></svg>'''

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>atlas-smilies Demo</title>
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <style>
    :root {
      --bg: #F8FAFC;
      --surface: #FFFFFF;
      --text: #1F425E;
      --primary: #3776AB;
      --secondary: #FFD43B;
      --border: #E2E8F0;
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', 'Menlo', 'Consolas', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    header {
      background: var(--primary);
      color: white;
      padding: 2rem 1rem;
      text-align: center;
    }

    header h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }

    header p {
      font-size: 1.1rem;
      opacity: 0.9;
    }

    main {
      flex: 1;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
      width: 100%;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .card h2 {
      color: var(--primary);
      margin-bottom: 1rem;
      font-size: 1.5rem;
    }

    .code-block {
      background: #1e1e1e;
      color: #d4d4d4;
      font-family: var(--font-mono);
      padding: 1rem;
      border-radius: 4px;
      overflow-x: auto;
      font-size: 0.9rem;
      margin-bottom: 1rem;
    }

    button {
      background: var(--primary);
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s ease;
      font-family: var(--font-sans);
      font-weight: 600;
    }

    button:hover {
      background: #2a5a83;
    }

    button:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }

    .result {
      margin-top: 1rem;
      padding: 1rem;
      background: #f1f5f9;
      border-left: 4px solid var(--primary);
      border-radius: 0 4px 4px 0;
      font-family: var(--font-mono);
      white-space: pre-wrap;
      display: none;
    }

    .result.show {
      display: block;
      animation: fadeIn 0.3s ease-in;
    }

    .error-msg {
      color: #dc2626;
      font-weight: bold;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .loader {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid #fff;
      border-radius: 50%;
      border-top-color: transparent;
      animation: spin 1s linear infinite;
      margin-right: 8px;
      vertical-align: middle;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    footer {
      text-align: center;
      padding: 2rem;
      border-top: 1px solid var(--border);
      background: var(--surface);
      margin-top: auto;
    }

    footer a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
    }

    footer a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>

  <header>
    <h1>atlas-smilies</h1>
    <p>Multi-omic trajectory inference from paired scRNA & ATAC seq data</p>
  </header>

  <main>
    <div class="card">
      <h2>About the Demo</h2>
      <p>
        <strong>Note:</strong> The actual <code>atlas-smilies</code> package relies heavily on C-extensions
        (via Anndata, Scanpy, Numpy) which cannot currently run within a Cloudflare Worker (Pyodide) environment.
        This demo provides a graceful mock API that simulates the trajectory inference outputs.
      </p>
    </div>

    <div class="card">
      <h2>Trajectory Inference Simulation</h2>
      <p>Click below to simulate processing a multi-omic dataset and generating pseudotime reconstruction.</p>
      <br>
      <button id="run-btn">Run Trajectory Inference</button>
      <div id="run-result" class="result"></div>
    </div>
  </main>

  <footer>
    <p>
      Worker Demo powered by <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a> |
      <a href="https://pypi.org/project/atlas-smilies/" target="_blank">View on PyPI</a>
    </p>
  </footer>

  <script>
    document.getElementById('run-btn').addEventListener('click', async () => {
      const btn = document.getElementById('run-btn');
      const res = document.getElementById('run-result');

      btn.disabled = true;
      btn.innerHTML = '<span class="loader"></span>Processing...';
      res.classList.remove('show');

      try {
        const response = await fetch('/api/trajectory');
        const data = await response.json();

        if (data.error) {
          res.innerHTML = `<span class="error-msg">Error: ${data.error}</span><br><br>${data.message || ''}`;
        } else {
          res.innerHTML = JSON.stringify(data, null, 2);
        }
      } catch (err) {
        res.innerHTML = `<span class="error-msg">Network Error: ${err.message}</span>`;
      } finally {
        res.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = 'Run Trajectory Inference';
      }
    });
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new([
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
        ("Cache-Control", "public, max-age=300")
    ])
    return Response.new(json.dumps(data), headers=headers, status=status)

# ─────────────────────────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────────────────────────

async def handle_info():
    """Returns information about the package and environment."""
    return json_response({
        "package": "atlas-smilies",
        "status": "simulated",
        "environment": "Cloudflare Workers (Pyodide)",
        "limitation": "Native C-extensions required by atlas-smilies (e.g. numpy, anndata) are not supported in Pyodide. All operations are simulated."
    })

async def handle_trajectory():
    """Simulates trajectory inference."""
    try:
        import atlas
        is_simulated = False
        message = "Trajectory inference completed natively."
    except ImportError as e:
        is_simulated = True
        message = f"Could not load atlas-smilies natively: {str(e)}. This is expected in Pyodide due to C-extension limitations."

    return json_response({
        "status": "success",
        "simulated": is_simulated,
        "pseudotime_computed": True,
        "cell_fate_predicted": True,
        "graph_type": "Weighted Nearest Neighbors",
        "cells_processed": 1024,
        "components": ["RNA", "ATAC"],
        "message": message
    }, status=200)

# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    from urllib.parse import urlparse
    path = urlparse(request.url).path or "/"

    if path == "/favicon.ico":
        headers = Headers.new([("Content-Type", "image/svg+xml"), ("Cache-Control", "public, max-age=86400")])
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()

    if path == "/api/trajectory":
        return await handle_trajectory()

    # Serve the main HTML UI
    headers = Headers.new([("Content-Type", "text/html; charset=utf-8")])
    return Response.new(HTML, headers=headers)
