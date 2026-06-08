import json
import os
import sys

from js import Response, Headers

# Mock pandas and numpy before importing atlaslevels to allow serverless execution without native binaries
from unittest.mock import MagicMock
sys.modules['numpy'] = MagicMock()
sys.modules['pandas'] = MagicMock()
pandas_mock = sys.modules['pandas']
pandas_mock.DataFrame = MagicMock
pandas_mock.Series = MagicMock

try:
    import atlaslevels
    import atlaslevels.validation
    ATLAS_IMPORTED = True
    ATLAS_ERROR = None
except Exception as e:
    ATLAS_IMPORTED = False
    ATLAS_ERROR = str(e)

# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new([
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
        ("Cache-Control", "public, max-age=300")
    ])
    return Response.new(json.dumps(data), headers=headers, status=status)

async def on_fetch(request, env):
    from urllib.parse import urlparse, parse_qsl
    parsed_url = urlparse(request.url)
    path = parsed_url.path or "/"
    qs = dict(parse_qsl(parsed_url.query))

    if path == "/api/info":
        return await handle_info()
    elif path == "/api/ontology":
        return await handle_ontology(qs)
    elif path == "/api/bundle":
        return await handle_bundle()
    elif path == "/api/validate":
        return await handle_validate()
    elif path == "/favicon.ico":
        headers = Headers.new([("Content-Type", "image/svg+xml"), ("Cache-Control", "public, max-age=86400")])
        return Response.new(FAVICON_SVG, headers=headers)
    else:
        headers = Headers.new([("Content-Type", "text/html; charset=utf-8")])
        return Response.new(HTML, headers=headers)

# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────



async def handle_info():
    if not ATLAS_IMPORTED:
        return json_response({"error": "Failed to load atlaslevels package", "details": ATLAS_ERROR}, status=500)

    return json_response({
        "status": "ok",
        "message": "atlaslevels package is loaded successfully.",
        "presets_ontology": list(atlaslevels.loaders._ONTOLOGY_PRESETS.keys()),
        "presets_bundle": list(atlaslevels.loaders._BUNDLE_PRESETS.keys())
    })

async def handle_ontology(qs):
    if not ATLAS_IMPORTED:
        return json_response({"error": "Failed to load atlaslevels package", "details": ATLAS_ERROR}, status=500)

    try:
        ont = atlaslevels.load_preset_ontology("allen_ccfv3")
        node_id_str = qs.get("id", str(ont.root_id))

        try:
            node_id = int(node_id_str)
        except ValueError:
            return json_response({"error": "Invalid node ID format. Must be an integer."}, status=400)

        try:
            node = ont.get_node(node_id)
            if node is None:
                return json_response({"error": f"Node with ID {node_id} not found."}, status=404)
            return json_response({
                "id": node.id,
                "name": node.name,
                "acronym": node.acronym,
                "color": node.color,
                "parent_id": node.parent_id
            })
        except Exception as e:
            return json_response({"error": f"Node not found: {e}"}, status=404)

    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def handle_bundle():
    if not ATLAS_IMPORTED:
        return json_response({"error": "Failed to load atlaslevels package", "details": ATLAS_ERROR}, status=500)

    try:
        bundle = atlaslevels.load_preset_bundle("allen_gm")
        levels = []
        for lvl in bundle.list_levels():
            levels.append({
                "level_name": lvl.level_name,
                "display_name": lvl.display_name,
                "level_index": lvl.level_index,
                "num_parents": len(lvl.parents)
            })

        return json_response({
            "levels": levels
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def handle_validate():
    if not ATLAS_IMPORTED:
        return json_response({"error": "Failed to load atlaslevels package", "details": ATLAS_ERROR}, status=500)

    try:
        ont = atlaslevels.load_preset_ontology("allen_ccfv3")
        bundle = atlaslevels.load_preset_bundle("allen_gm")
        result = atlaslevels.validation.validate_bundle(bundle, ont)

        return json_response({
            "valid": len(result.issues) == 0,
            "issues": [str(issue) for issue in result.issues]
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

# ─────────────────────────────────────────────────────────────────────────────
# HTML / UI
# ─────────────────────────────────────────────────────────────────────────────

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#2d3748"/>
  <path d="M50 20 L80 80 L20 80 Z" fill="#4fd1c5" opacity="0.8"/>
  <circle cx="50" cy="50" r="15" fill="#f6ad55"/>
</svg>"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>atlaslevels Demo</title>
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <style>
    :root {
      --bg: #f8fafc; --text: #0f172a; --panel: #ffffff;
      --primary: #0284c7; --border: #e2e8f0; --muted: #64748b;
      --success: #10b981; --error: #ef4444;
    }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      margin: 0; background: var(--bg); color: var(--text);
      line-height: 1.5;
    }
    .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
    header { text-align: center; margin-bottom: 2rem; }
    h1 { margin: 0 0 0.5rem; color: var(--primary); }
    .panel {
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      transition: transform 0.2s;
    }
    .panel:hover { transform: translateY(-2px); }
    h2 { margin-top: 0; font-size: 1.25rem; }
    button {
      background: var(--primary); color: white; border: none;
      padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;
      font-weight: 500; transition: opacity 0.2s;
    }
    button:hover { opacity: 0.9; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    input {
      padding: 0.5rem; border: 1px solid var(--border);
      border-radius: 4px; margin-right: 0.5rem;
    }
    pre {
      background: #1e293b; color: #e2e8f0; padding: 1rem;
      border-radius: 4px; overflow-x: auto; font-size: 0.875rem;
      margin-top: 1rem; display: none;
    }
    pre.show { display: block; animation: fadeIn 0.3s; }
    .spinner {
      display: inline-block; width: 1rem; height: 1rem;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%; border-top-color: white;
      animation: spin 1s linear infinite; margin-right: 0.5rem;
      vertical-align: text-bottom;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    footer {
      text-align: center; margin-top: 3rem; padding-top: 1rem;
      border-top: 1px solid var(--border); color: var(--muted);
      font-size: 0.875rem;
    }
    a { color: var(--primary); text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>atlaslevels Demo</h1>
      <p>Interactive Cloudflare Worker demo for <a href="https://pypi.org/project/atlaslevels/" target="_blank">atlaslevels</a></p>
    </header>

    <div class="panel">
      <h2>Environment Info</h2>
      <button id="btn-info" onclick="fetchData('/api/info', 'out-info', this)">Load Info</button>
      <pre id="out-info"></pre>
    </div>

    <div class="panel">
      <h2>Ontology Node Explorer</h2>
      <p style="color:var(--muted);font-size:0.875rem;margin-top:0;">Preset: <code>allen_ccfv3</code></p>
      <input type="number" id="node-id" placeholder="Node ID (e.g. 8)">
      <button id="btn-ont" onclick="loadOntology(this)">Query Node</button>
      <pre id="out-ont"></pre>
    </div>

    <div class="panel">
      <h2>Hierarchy Bundle Viewer</h2>
      <p style="color:var(--muted);font-size:0.875rem;margin-top:0;">Preset: <code>allen_gm</code></p>
      <button id="btn-bundle" onclick="fetchData('/api/bundle', 'out-bundle', this)">Load Bundle Levels</button>
      <pre id="out-bundle"></pre>
    </div>

    <div class="panel">
      <h2>Validation</h2>
      <button id="btn-val" onclick="fetchData('/api/validate', 'out-val', this)">Validate GM Bundle</button>
      <pre id="out-val"></pre>
    </div>

    <footer>
      Powered by <a href="https://pypi.org/project/atlaslevels/" target="_blank">atlaslevels</a> |
      <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
    </footer>
  </div>

  <script>
    async function fetchData(url, outId, btn) {
      const out = document.getElementById(outId);
      btn.disabled = true;
      const oldHtml = btn.innerHTML;
      btn.innerHTML = '<span class="spinner"></span>Loading...';
      out.classList.remove('show');

      try {
        const res = await fetch(url);
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        out.textContent = 'Error: ' + e.message;
      } finally {
        out.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = oldHtml;
      }
    }

    function loadOntology(btn) {
      const id = document.getElementById('node-id').value;
      const url = '/api/ontology' + (id ? '?id=' + id : '');
      fetchData(url, 'out-ont', btn);
    }
  </script>
</body>
</html>
"""


