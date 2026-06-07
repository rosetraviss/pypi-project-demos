import json
import urllib.parse
from js import Response, Headers, fetch as js_fetch

async def get_cone_search(ra, dec, radius_arcsec, limit=5):
    url = f"https://mmdc.am/api/observations/cone_search/?ra={ra}&dec={dec}&radius_arcsec={radius_arcsec}&limit={limit}"
    res = await js_fetch(url)
    data = await res.json()
    if hasattr(data, "to_py"):
        data = data.to_py()
    return data

async def get_infer(z, ebl, model_type, parameters):
    url = "https://mmdc.am/api/modeling/inference/"
    payload = {
        "z": z,
        "ebl": ebl,
        "model_type": model_type,
        "parameters": parameters,
    }
    headers = Headers.new({"Content-Type": "application/json"}.items())
    res = await js_fetch(url, method="POST", headers=headers, body=json.dumps(payload))
    data = await res.json()
    if hasattr(data, "to_py"):
        data = data.to_py()
    if isinstance(data, dict):
        return data.get("data", {}).get("best", data)
    return data

# ─────────────────────────────────────────────────────────────────────────────
# Assets
# ─────────────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>astro-mmdc Demo</title>
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --bg: #0f172a;
            --surface: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --success: #10b981;
            --error: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            flex-grow: 1;
        }

        header {
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.5s ease-out;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        p {
            color: var(--text-muted);
        }

        .card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 0.75rem;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            animation: fadeIn 0.5s ease-out;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        h2 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--text);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-muted);
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 0.75rem;
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            color: var(--text);
            font-size: 1rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }

        .row {
            display: flex;
            gap: 1rem;
        }

        .col {
            flex: 1;
        }

        button {
            width: 100%;
            padding: 0.75rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s;
        }

        button:hover {
            background-color: var(--primary-hover);
        }

        button:active {
            transform: scale(0.98);
        }

        button:disabled {
            background-color: var(--border);
            cursor: not-allowed;
            transform: none;
        }

        .result {
            margin-top: 1.5rem;
            padding: 1rem;
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            display: none;
            animation: fadeIn 0.3s ease-out;
        }

        .result.success {
            border-left: 4px solid var(--success);
        }

        .result.error {
            border-left: 4px solid var(--error);
        }

        .loader {
            display: none;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin: 0 auto;
        }

        .button-content {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        footer {
            text-align: center;
            padding: 2rem;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            margin-top: auto;
        }

        footer a {
            color: var(--primary);
            text-decoration: none;
            transition: color 0.2s;
        }

        footer a:hover {
            color: var(--primary-hover);
            text-decoration: underline;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>astro-mmdc</h1>
            <p>Astrophysical Database Query & Emission Modeling</p>
        </header>

        <div class="card">
            <h2>Cone Search</h2>
            <p style="margin-bottom: 1rem;">Query astrophysical databases for observations around specific coordinates.</p>
            <form id="search-form">
                <div class="row">
                    <div class="col form-group">
                        <label for="ra">Right Ascension (RA)</label>
                        <input type="number" id="ra" step="any" placeholder="e.g. 83.63" required>
                    </div>
                    <div class="col form-group">
                        <label for="dec">Declination (DEC)</label>
                        <input type="number" id="dec" step="any" placeholder="e.g. 22.01" required>
                    </div>
                    <div class="col form-group">
                        <label for="radius">Radius (arcsec)</label>
                        <input type="number" id="radius" step="any" value="5.0" required>
                    </div>
                </div>
                <button type="submit" id="search-btn">
                    <div class="button-content">
                        <span class="btn-text">Search</span>
                        <div class="loader" id="search-loader"></div>
                    </div>
                </button>
            </form>
            <div class="result" id="search-result"></div>
        </div>

        <div class="card">
            <h2>SSC Modeling</h2>
            <p style="margin-bottom: 1rem;">Run synchronous model inference (Synchrotron Self-Compton).</p>
            <form id="model-form">
                <div class="row">
                    <div class="col form-group">
                        <label for="z">Redshift (z)</label>
                        <input type="number" id="z" step="any" value="0.1" required>
                    </div>
                    <div class="col form-group">
                        <label for="log_b">log_B</label>
                        <input type="number" id="log_b" step="any" value="-1.0" required>
                    </div>
                </div>
                <button type="submit" id="model-btn">
                    <div class="button-content">
                        <span class="btn-text">Run Inference</span>
                        <div class="loader" id="model-loader"></div>
                    </div>
                </button>
            </form>
            <div class="result" id="model-result"></div>
        </div>
    </div>

    <footer>
        <p>Powered by <a href="https://pypi.org/project/astro-mmdc/" target="_blank">astro-mmdc</a></p>
        <p>A package from <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a></p>
    </footer>

    <script>
        const setupForm = (formId, btnId, loaderId, resultId, endpoint, dataMapper) => {
            const form = document.getElementById(formId);
            const btn = document.getElementById(btnId);
            const loader = document.getElementById(loaderId);
            const result = document.getElementById(resultId);
            const btnText = btn.querySelector('.btn-text');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Loading state
                btn.disabled = true;
                btnText.style.display = 'none';
                loader.style.display = 'block';
                result.style.display = 'none';
                result.className = 'result';

                try {
                    const data = dataMapper();
                    const params = new URLSearchParams(data);

                    const response = await fetch(`${endpoint}?${params}`);
                    const json = await response.json();

                    result.textContent = JSON.stringify(json, null, 2);
                    result.classList.add(response.ok ? 'success' : 'error');
                } catch (err) {
                    result.textContent = `Error: ${err.message}`;
                    result.classList.add('error');
                } finally {
                    // Reset state
                    result.style.display = 'block';
                    btn.disabled = false;
                    btnText.style.display = 'block';
                    loader.style.display = 'none';
                }
            });
        };

        // Setup Cone Search
        setupForm('search-form', 'search-btn', 'search-loader', 'search-result', '/api/query', () => ({
            ra: document.getElementById('ra').value,
            dec: document.getElementById('dec').value,
            radius: document.getElementById('radius').value
        }));

        // Setup SSC Modeling
        setupForm('model-form', 'model-btn', 'model-loader', 'model-result', '/api/model', () => ({
            z: document.getElementById('z').value,
            log_b: document.getElementById('log_b').value
        }));
    </script>
</body>
</html>
"""

SVG_FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#0f172a"/>
  <circle cx="50" cy="50" r="30" fill="none" stroke="#3b82f6" stroke-width="4"/>
  <circle cx="50" cy="20" r="8" fill="#60a5fa"/>
  <circle cx="24" cy="65" r="5" fill="#93c5fd"/>
  <circle cx="76" cy="65" r="4" fill="#93c5fd"/>
  <path d="M50 50 L50 20 M50 50 L24 65 M50 50 L76 65" stroke="#334155" stroke-width="2" stroke-dasharray="4 4"/>
</svg>"""

LLMS_TXT = """# astro-mmdc Demo

A Cloudflare Python Worker demonstrating the `astro-mmdc` package capabilities.

This simple demo provides a web interface with endpoints to use the `astro-mmdc` package, allowing query and simple modeling operations. The API endpoints interact with the `astro_mmdc` python module to perform cone searches for observations and generate emission modeling simulations.
"""

LLMS_FULL_TXT = """# astro-mmdc Demo Detailed Information

A Cloudflare Python Worker demonstrating the `astro-mmdc` package capabilities.

This simple demo provides a web interface with endpoints to use the `astro-mmdc` package, allowing query and simple modeling operations. The API endpoints interact with the `astro_mmdc` python module to perform cone searches for observations and generate emission modeling simulations.

Endpoints typically exposed:
- `/api/query`: Endpoint to run cone searches using RA and DEC coordinates.
- `/api/model`: Endpoint to run synchronous model inference (e.g., SSC type).
"""

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def create_response(body, status=200, content_type="application/json"):
    headers = Headers.new({"content-type": content_type}.items())
    headers.append("Access-Control-Allow-Origin", "*")
    return Response.new(body, status=status, headers=headers)

# ─────────────────────────────────────────────────────────────────────────────
# Worker Handler
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url = urllib.parse.urlparse(request.url)
    path = url.path

    if path == "/" or path == "/index.html":
        return create_response(HTML, content_type="text/html")

    if path == "/favicon.svg":
        return create_response(SVG_FAVICON, content_type="image/svg+xml")

    if path == "/llms.txt":
        return create_response(LLMS_TXT, content_type="text/plain")

    if path == "/llms-full.txt":
        return create_response(LLMS_FULL_TXT, content_type="text/plain")

    if path == "/api/query":
        query = urllib.parse.parse_qs(url.query)
        try:
            ra = float(query.get("ra", [0.0])[0])
            dec = float(query.get("dec", [0.0])[0])
            radius = float(query.get("radius", [5.0])[0])

            try:
                results = await get_cone_search(ra=ra, dec=dec, radius_arcsec=radius, limit=5)
                return create_response(json.dumps(results))
            except Exception as e:
                return create_response(json.dumps({"error": str(e), "note": "MMDC client connection or query failed"}), status=500)

        except ValueError as e:
            return create_response(json.dumps({"error": f"Invalid parameters: {e}"}), status=400)

    if path == "/api/model":
        query = urllib.parse.parse_qs(url.query)
        try:
            z = float(query.get("z", [0.1])[0])
            log_b = float(query.get("log_b", [-1.0])[0])

            try:
                params = {
                    "log_B": log_b,
                    "log_electron_luminosity": 42.0,
                    "log_gamma_cut": 4.0,
                    "log_gamma_min": 1.0,
                    "log_radius": 16.0,
                    "lorentz_factor": 10.0,
                    "spectral_index": 2.0
                }

                result = await get_infer(z=z, ebl=False, model_type="SSC", parameters=params)
                return create_response(json.dumps(result))

            except Exception as e:
                return create_response(json.dumps({"error": str(e), "note": "MMDC modeling failed"}), status=500)

        except ValueError as e:
            return create_response(json.dumps({"error": f"Invalid parameters: {e}"}), status=400)

    return create_response(json.dumps({"error": "Not found"}), status=404)
