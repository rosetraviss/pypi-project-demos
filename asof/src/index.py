import json
from datetime import datetime, timezone
from pyodide.ffi import to_js
from js import Response, Headers


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>asof - Historical Package Lookup</title>
  <style>
    :root {
      --bg: #fafafa;
      --fg: #111;
      --accent: #2563eb;
      --card-bg: #fff;
      --border: #e5e5e5;
      --muted: #666;
      --error: #ef4444;
      --success: #10b981;
    }

    * { box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--fg);
      line-height: 1.5;
      margin: 0;
      padding: 0;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
    }

    h1 {
      font-size: 2.5rem;
      margin-bottom: 10px;
      letter-spacing: -0.05em;
    }

    .subtitle {
      color: var(--muted);
      font-size: 1.1rem;
      max-width: 600px;
      margin: 0 auto;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
      margin-bottom: 30px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      font-weight: 500;
      margin-bottom: 8px;
    }

    input[type="text"], input[type="date"] {
      width: 100%;
      padding: 12px 16px;
      font-size: 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    button {
      background: var(--accent);
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 1rem;
      font-weight: 500;
      border-radius: 8px;
      cursor: pointer;
      width: 100%;
      transition: background-color 0.2s, transform 0.1s;
    }

    button:hover {
      background: #1d4ed8;
    }

    button:active {
      transform: translateY(1px);
    }

    button:disabled {
      background: #93c5fd;
      cursor: not-allowed;
    }

    .result-container {
      margin-top: 24px;
      padding: 20px;
      border-radius: 8px;
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
    }

    .result-item:last-child {
      border-bottom: none;
    }

    .result-label {
      font-weight: 500;
      color: var(--muted);
    }

    .result-value {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 600;
    }

    .error-msg {
      color: var(--error);
      padding: 12px;
      background: #fef2f2;
      border-radius: 6px;
      border: 1px solid #fecaca;
      display: none;
      margin-top: 16px;
    }

    .spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(255,255,255,0.3);
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
      padding-top: 20px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.9rem;
    }

    footer a {
      color: var(--accent);
      text-decoration: none;
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
           <span class="result-value" id="res-source" style="font-size: 0.85em; margin-top: 4px; word-break: break-all; font-weight: normal; color: var(--accent);"></span>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>API Usage</h3>
      <p>You can also use this service via an API endpoint:</p>
      <pre style="background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; overflow-x: auto;"><code>curl "https://asof.pypi.rosetraviss.uk/api/asof?package=requests&date=2021-01-01"</code></pre>
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
    query = {}
    if "?" in url_str:
        qs = url_str.split("?", 1)[1].split("#")[0]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query[k] = v
    return query

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

    if not date_str:
        return json_response({"error": "Missing 'date' parameter (format: YYYY-MM-DD)"}, status=400)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # Call the PyPI API directly using pyfetch
        from pyodide.http import pyfetch
        import asof
        import json
        from collections import defaultdict
        import datetime as dt
        from packaging.version import Version
        from packaging.version import VERSION_PATTERN as version_pattern_str
        import re

        url = f"https://pypi.org/simple/{pkg}/"
        resp = await pyfetch(url, headers={"Accept": "application/vnd.pypi.simple.v1+json"})

        if resp.status == 404:
            return json_response({"error": f"Package '{pkg}' not found on PyPI"}, status=404)

        if not resp.ok:
            return json_response({"error": f"{resp.status}: {resp.status_text} when attempting to query PyPI"}, status=502)

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

        from asof.pypi import is_compatible

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
        print(f"Error handling request: {e}\n{traceback.format_exc()}")
        return json_response({"error": "An unexpected error occurred while processing your request."}, status=500)

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
