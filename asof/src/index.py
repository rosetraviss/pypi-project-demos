import json
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from js import Response, Headers


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>asof - Historical Package Lookup</title>
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #145d91;
      --primary-hover: #3776ab;
      --bg: #f7f9ff;
      --fg: #001d32;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --muted: #41474f;
      --error: #ba1a1a;
      --success: #316600;
      
      --font-sans: 'Inter', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--fg);
      line-height: 1.5;
      padding: 0;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 48px 24px;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
    }

    h1 {
      font-size: 36px;
      font-weight: 700;
      line-height: 44px;
      letter-spacing: -0.02em;
      font-family: var(--font-mono);
      color: var(--fg);
      margin-bottom: 8px;
    }

    .subtitle {
      color: var(--muted);
      font-size: 16px;
      line-height: 24px;
      max-width: 600px;
      margin: 0 auto;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .card:hover {
      box-shadow: 0 4px 12px rgba(31, 66, 94, 0.08);
    }
    
    .card h3 {
      font-size: 20px;
      font-weight: 600;
      line-height: 28px;
      margin-bottom: 16px;
      font-family: var(--font-sans);
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      line-height: 16px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }

    input[type="text"], input[type="date"] {
      width: 100%;
      padding: 10px 14px;
      font-size: 14px;
      font-family: var(--font-sans);
      border: 1px solid var(--border);
      border-radius: 4px;
      background-color: #f8fafc;
      color: var(--fg);
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(20, 93, 145, 0.15);
    }

    button {
      background: var(--primary);
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      width: 100%;
      transition: background-color 0.2s, transform 0.1s;
    }

    button:hover {
      background: var(--primary-hover);
    }

    button:active {
      transform: translateY(1px);
    }

    button:disabled {
      background: #98cbff;
      cursor: not-allowed;
    }

    .result-container {
      margin-top: 24px;
      padding: 20px;
      border-radius: 4px;
      background: #f8fafc;
      border: 1px solid var(--border);
      display: none;
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .result-container.show {
      display: block;
      opacity: 1;
    }

    .result-item {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid var(--border);
      font-size: 14px;
    }

    .result-item:last-child {
      border-bottom: none;
    }

    .result-label {
      font-weight: 500;
      color: var(--muted);
    }

    .result-value {
      font-family: var(--font-mono);
      font-weight: 600;
      color: var(--fg);
    }

    .error-msg {
      color: var(--error);
      padding: 12px;
      background: #ffdad6;
      border-radius: 4px;
      border: 1px solid var(--border);
      display: none;
      margin-top: 16px;
      font-size: 14px;
    }

    .spinner {
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 1s ease-in-out infinite;
      vertical-align: middle;
      margin-right: 8px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    footer {
      text-align: center;
      margin-top: 60px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
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
  <div class="container">
    <header>
      <h1>asof</h1>
      <p class="subtitle">Query PyPI package versions as of a specific historical date.</p>
    </header>

    <div class="card">
      <div class="form-group">
        <label for="package-name">Package Name</label>
        <input type="text" id="package-name" placeholder="e.g., requests, pandas, numpy" required>
      </div>

      <div class="form-group">
        <label for="asof-date">As of Date</label>
        <input type="date" id="asof-date" required>
      </div>

      <button id="lookup-btn" onclick="lookupPackage()">Lookup Version</button>

      <div id="error-message" class="error-msg"></div>

      <div id="result-box" class="result-container">
        <div class="result-item">
          <span class="result-label">Package</span>
          <span class="result-value" id="res-package"></span>
        </div>
        <div class="result-item">
          <span class="result-label">Version</span>
          <span class="result-value" id="res-version"></span>
        </div>
        <div class="result-item">
          <span class="result-label">Release Date</span>
          <span class="result-value" id="res-date"></span>
        </div>
        <div class="result-item" style="display: flex; flex-direction: column; align-items: flex-start;">
           <span class="result-label">Source</span>
           <span class="result-value" id="res-source" style="font-size: 0.85em; margin-top: 4px; word-break: break-all; font-weight: normal; color: var(--primary);"></span>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>API Usage</h3>
      <p style="font-size: 14px; color: var(--muted); margin-bottom: 12px;">You can also use this service via an API endpoint:</p>
      <pre style="background: #f8fafc; color: #001d32; border: 1px solid var(--border); padding: 14px 16px; border-radius: 8px; overflow-x: auto; font-family: var(--font-mono); font-size: 14px; line-height: 22px;"><code>curl "https://asof.pypi.rosetraviss.uk/api/asof?package=requests&date=2021-01-01"</code></pre>
    </div>

    <footer>
      Powered by the <a href="https://pypi.rosetraviss.uk/asof" target="_blank">asof</a> library on Cloudflare Python Workers. Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
    </footer>
  </div>

  <script>
    // Set default date to today
    document.getElementById('asof-date').valueAsDate = new Date();

    // Allow enter key to trigger lookup
    document.getElementById('package-name').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') lookupPackage();
    });

    async function lookupPackage() {
      const btn = document.getElementById('lookup-btn');
      const pkg = document.getElementById('package-name').value.trim();
      const date = document.getElementById('asof-date').value;
      const resultBox = document.getElementById('result-box');
      const errorMsg = document.getElementById('error-message');

      if (!pkg || !date) {
        showError("Please enter both a package name and a date.");
        return;
      }

      errorMsg.style.display = 'none';
      resultBox.classList.remove('show');

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>Looking up...';

      try {
        const response = await fetch(`/api/asof?package=${encodeURIComponent(pkg)}&date=${encodeURIComponent(date)}`);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to lookup package");
        }

        if (data.matches && data.matches.length > 0) {
          const match = data.matches[0];
          document.getElementById('res-package').textContent = match.package;
          document.getElementById('res-version').textContent = match.version;

          // Format date nicely
          const releaseDate = new Date(match.date);
          document.getElementById('res-date').textContent = releaseDate.toLocaleDateString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
          });

          const sourceEl = document.getElementById('res-source');
          sourceEl.textContent = match.source;

          resultBox.classList.add('show');
        } else {
          showError(data.message || `No version found for ${pkg} as of ${date}`);
        }

      } catch (err) {
        showError(err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = 'Lookup Version';
      }
    }

    function showError(msg) {
      const errorMsg = document.getElementById('error-message');
      errorMsg.textContent = msg;
      errorMsg.style.display = 'block';
      document.getElementById('result-box').classList.remove('show');
    }
  </script>
</body>
</html>"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#2563eb" />
  <text x="50" y="65" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">A</text>
</svg>"""

def parse_qs(url_str: str) -> dict:
    """Extract query parameters from a URL string."""
    from urllib.parse import urlparse, parse_qsl
    try:
        return dict(parse_qsl(urlparse(url_str).query))
    except Exception:
        return {}

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)


async def handle_asof(query: dict):
    pkg = query.get("package")
    date_str = query.get("date")

    if not pkg:
        return json_response({"error": "Missing 'package' parameter"}, status=400)

    import re
    if not re.match(r"^[a-zA-Z0-9-_.]+$", pkg):
        return json_response({"error": "Invalid package name format"}, status=400)

    if not date_str:
        return json_response({"error": "Missing 'date' parameter (format: YYYY-MM-DD)"}, status=400)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # Call the PyPI API directly using pyfetch
        # pyrefly: ignore [missing-import]
        from pyodide.http import pyfetch
        import sys
        from types import ModuleType
        
        # Mock rich.status to prevent thread creation which is unsupported in Cloudflare Pyodide Workers
        class DummyStatus:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args, **kwargs): pass
            def start(self): pass
            def stop(self): pass
            
        rich_status = ModuleType("rich.status")
        rich_status.Status = DummyStatus
        sys.modules["rich.status"] = rich_status

        # Mock subprocess.run to raise FileNotFoundError as subprocesses are not supported in WebAssembly/Pyodide
        import subprocess
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("Subprocesses are not supported in Emscripten/Pyodide")
        subprocess.run = mock_run

        # pyrefly: ignore [missing-import]
        import asof
        import json
        from collections import defaultdict
        import datetime as dt
        # pyrefly: ignore [missing-import]
        from packaging.version import Version
        # pyrefly: ignore [missing-import]
        from packaging.version import VERSION_PATTERN as version_pattern_str
        import re

        url = f"https://pypi.org/simple/{pkg}/"
        resp = await pyfetch(url, headers={"Accept": "application/vnd.pypi.simple.v1+json"})

        if not resp.ok:
            return json_response({"error": f"{resp.status}: {resp.status_text} when attempting to query PyPI"}, status=500)

        json_data = await resp.string()
        file_objs = json.loads(json_data)["files"]

        version_pattern = re.compile(version_pattern_str, re.VERBOSE | re.IGNORECASE)
        grouped = defaultdict(list)
        for file_obj in file_objs:
            m = version_pattern.search(file_obj["filename"])
            if m:
                version_str = m.group(0)
                grouped[version_str].append(file_obj)

        version_strs = sorted(grouped.keys(), key=Version)
        version_strs.reverse()

        from asof.pypi import is_compatible # pyrefly: ignore [missing-import]

        matches = []
        for version_str in version_strs:
            for file_obj in grouped[version_str]:
                if file_obj["yanked"]:
                    continue

                dt_obj = dt.datetime.fromisoformat(file_obj["upload-time"])
                if dt_obj > parsed_date:
                    continue

                version_obj = is_compatible(file_obj)
                if version_obj is None:
                    continue

                if version_obj.is_prerelease and matches:
                    continue

                matches.append({
                    "package": pkg,
                    "version": str(version_obj),
                    "date": dt_obj.isoformat(),
                    "source": "https://pypi.org"
                })

                if not version_obj.is_prerelease:
                    break

            if len(matches) > 0 and not Version(matches[-1]["version"]).is_prerelease:
                break

        if matches:
            return json_response({
                "package": pkg,
                "as_of_date": date_str,
                "matches": matches,
                "message": None
            })
        else:
            return json_response({
                "package": pkg,
                "as_of_date": date_str,
                "matches": [],
                "message": f"No compatible releases or prereleases on PyPI as of {parsed_date.isoformat()} for package {pkg}"
            })

    except ValueError as e:
        if "time data" in str(e):
            return json_response({"error": f"Invalid date format: {date_str} (use YYYY-MM-DD)"}, status=400)
        return json_response({"error": str(e)}, status=400)
    except Exception as e:
        import traceback
        return json_response({"error": str(e), "traceback": traceback.format_exc()}, status=500)

async def on_fetch(request, env):
    url = str(request.url)
    qs = parse_qs(url)
    path = url.split("?")[0]

    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/asof":
        return await handle_asof(qs)

    # Default to returning the HTML interface
    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
