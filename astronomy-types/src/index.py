import json
import traceback
from js import Headers, Response

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="#4f46e5"/><path d="M50 15 L60 40 L85 45 L65 60 L70 85 L50 70 L30 85 L35 60 L15 45 L40 40 Z" fill="#fff"/></svg>"""


STYLE_CSS = """:root {
  --primary: #145d91;
  --primary-hover: #3776ab;
  --bg: #f7f9ff;
  --surface: #ffffff;
  --text: #001d32;
  --text-muted: #41474f;
  --border: #e2e8f0;
  --success-bg: #ebffd5;
  --success-text: #316600;
  --error-bg: #ffdad6;
  --error-text: #ba1a1a;
  
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.5;
  padding: 48px 24px;
}

.container { max-width: 800px; margin: 0 auto; }

header { text-align: center; margin-bottom: 40px; }
h1 {
  font-family: var(--font-mono);
  font-size: 36px;
  font-weight: 700;
  line-height: 44px;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}
.subtitle { color: var(--text-muted); font-size: 16px; }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  box-shadow: 0 4px 12px rgba(31, 66, 94, 0.08);
}
h2 {
  font-size: 20px;
  font-weight: 600;
  line-height: 28px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.info-item { background: #f8fafc; padding: 16px; border-radius: 4px; font-size: 14px; border: 1px solid var(--border); }

.tabs { display: flex; gap: 8px; margin-bottom: 24px; border-bottom: 1px solid var(--border); }
.tab {
  padding: 10px 16px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-muted);
  transition: all 0.2s ease;
}
.tab:hover { color: var(--text); background: rgba(20, 93, 145, 0.05); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }

.tab-content { display: none; animation: fadeIn 0.3s ease; }
.tab-content.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.input-group { margin-bottom: 16px; }
.input-group.row { display: flex; gap: 16px; }
.col { flex: 1; }
label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 8px;
  color: var(--text-muted);
}
input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 14px;
  background-color: #f8fafc;
  color: var(--text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(20, 93, 145, 0.15); }

.action-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}
.action-btn:hover { background: var(--primary-hover); }
.action-btn:active { transform: scale(0.98); }

.result-panel {
  margin-top: 24px;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid var(--border);
  display: none;
}
.result-panel.show { display: block; animation: slideDown 0.3s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.success { background: var(--success-bg); color: var(--success-text); padding: 12px; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
.error { background: var(--error-bg); color: var(--error-text); padding: 12px; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
.meta { font-size: 12px; color: var(--text-muted); text-align: center; }
code { background: #f8fafc; padding: 2px 4px; border-radius: 4px; font-family: var(--font-mono); font-size: 12px; border: 1px solid var(--border); }

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

footer {
  text-align: center;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  font-size: 14px;
  color: var(--text-muted);
}
footer a { color: var(--primary); text-decoration: none; font-weight: 600; }
footer a:hover { text-decoration: underline; }
footer p { margin-bottom: 8px; }
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>astronomy-types Cloudflare Worker Demo</title>
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <div class="container">
    <header>
      <h1>astronomy-types Demo</h1>
      <p class="subtitle">Cloudflare Python Worker running Pyodide</p>
    </header>

    <main>
      <section class="card">
        <h2>Package Info</h2>
        <div id="pkg-info" class="info-grid">
          <div class="spinner"></div>
        </div>
      </section>

      <section class="card">
        <h2>Conversion Tools</h2>

        <div class="tabs">
          <button class="tab active" data-target="deg-to-hrs">Degrees to Hours</button>
          <button class="tab" data-target="dms-to-deg">DMS to Degrees</button>
          <button class="tab" data-target="hms-to-deg">HMS to Degrees</button>
        </div>

        <!-- Degrees to Hours -->
        <div id="deg-to-hrs" class="tab-content active">
          <div class="input-group">
            <label for="deg-input">Degrees (e.g. 180.5)</label>
            <input type="number" id="deg-input" step="any" placeholder="Enter degrees">
          </div>
          <button onclick="convertDegToHrs()" class="action-btn">Convert</button>
          <div id="res-deg-to-hrs" class="result-panel"></div>
        </div>

        <!-- DMS to Degrees -->
        <div id="dms-to-deg" class="tab-content">
          <div class="input-group row">
            <div class="col">
              <label>Degrees</label>
              <input type="number" id="dms-d" placeholder="D">
            </div>
            <div class="col">
              <label>Minutes</label>
              <input type="number" id="dms-m" placeholder="M">
            </div>
            <div class="col">
              <label>Seconds</label>
              <input type="number" id="dms-s" step="any" placeholder="S">
            </div>
          </div>
          <button onclick="convertDmsToDeg()" class="action-btn">Convert</button>
          <div id="res-dms-to-deg" class="result-panel"></div>
        </div>

        <!-- HMS to Degrees -->
        <div id="hms-to-deg" class="tab-content">
          <div class="input-group row">
            <div class="col">
              <label>Hours</label>
              <input type="number" id="hms-h" placeholder="H">
            </div>
            <div class="col">
              <label>Minutes</label>
              <input type="number" id="hms-m" placeholder="M">
            </div>
            <div class="col">
              <label>Seconds</label>
              <input type="number" id="hms-s" step="any" placeholder="S">
            </div>
          </div>
          <button onclick="convertHmsToDeg()" class="action-btn">Convert</button>
          <div id="res-hms-to-deg" class="result-panel"></div>
        </div>

      </section>
    </main>

    <footer>
      <p>Powered by <a href="https://pypi.rosetraviss.uk" target="_blank" rel="noopener">pypi.rosetraviss.uk</a></p>
      <p><a href="https://pypi.rosetraviss.uk/astronomy-types" target="_blank" rel="noopener">astronomy-types on PyPI Mirror</a></p>
    </footer>
  </div>

  <script>
    // Tab switching logic
    document.querySelectorAll('.tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.target).classList.add('active');
      });
    });

    // Fetch Info
    async function loadInfo() {
      try {
        const res = await fetch('/api/info');
        const data = await res.json();
        const grid = document.getElementById('pkg-info');
        if (data.error) throw new Error(data.error);

        grid.innerHTML = `
          <div class="info-item"><strong>Available Functions:</strong> \${data.functions.length}</div>
          <div class="info-item"><strong>Selected Conversions:</strong> \${data.functions.filter(f => f.includes('to_')).join(', ')}</div>
        `;
      } catch (err) {
        const grid = document.getElementById('pkg-info');
        grid.innerHTML = '<div class="error">Error loading info: <span class="err-msg"></span></div>';
        grid.querySelector('.err-msg').textContent = err.message;
      }
    }

    async function doFetch(url, resultElId) {
      const el = document.getElementById(resultElId);
      el.innerHTML = '<div class="spinner"></div>';
      el.classList.add('show');
      try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        el.innerHTML = '<div class="success"><strong>Result:</strong> <span class="res-val"></span></div><div class="meta"><code class="call-val"></code></div>';
        el.querySelector('.res-val').textContent = data.result;
        el.querySelector('.call-val').textContent = data.call;
      } catch (err) {
        el.innerHTML = '<div class="error"></div>';
        el.querySelector('.error').textContent = err.message;
      }
    }

    function convertDegToHrs() {
      const v = document.getElementById('deg-input').value;
      if (!v) return;
      doFetch(\`/api/convert?type=deg_to_hrs&deg=\${v}\`, 'res-deg-to-hrs');
    }

    function convertDmsToDeg() {
      const d = document.getElementById('dms-d').value || 0;
      const m = document.getElementById('dms-m').value || 0;
      const s = document.getElementById('dms-s').value || 0;
      doFetch(\`/api/convert?type=dms_to_deg&d=\${d}&m=\${m}&s=\${s}\`, 'res-dms-to-deg');
    }

    function convertHmsToDeg() {
      const h = document.getElementById('hms-h').value || 0;
      const m = document.getElementById('hms-m').value || 0;
      const s = document.getElementById('hms-s').value || 0;
      doFetch(\`/api/convert?type=hms_to_deg&h=\${h}&m=\${m}&s=\${s}\`, 'res-hms-to-deg');
    }

    // Init
    loadInfo();
  </script>
</body>
</html>
"""

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

def parse_qs(url_str: str) -> dict:
    from urllib.parse import urlparse, parse_qsl
    return dict(parse_qsl(urlparse(url_str).query))

async def handle_info():
    try:
        import astronomy_types
        all_attrs = dir(astronomy_types)
        funcs = [f for f in all_attrs if callable(getattr(astronomy_types, f)) and not f.startswith("_")]

        return json_response({
            "package": "astronomy-types",
            "functions": funcs,
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def handle_convert(qs: dict):
    try:
        import astronomy_types
        conv_type = qs.get("type")

        if conv_type == "deg_to_hrs":
            deg = float(qs.get("deg", 0))
            res = astronomy_types.degrees_to_hours(deg)
            return json_response({
                "result": float(res),
                "call": f"degrees_to_hours({deg})"
            })

        elif conv_type == "dms_to_deg":
            d = int(qs.get("d", 0))
            m = int(qs.get("m", 0))
            s = float(qs.get("s", 0))
            # dms_to_degrees takes a DMS object
            dms = astronomy_types.DMS(d, m, s)
            res = astronomy_types.dms_to_degrees(dms)
            return json_response({
                "result": float(res),
                "call": f"dms_to_degrees(DMS({d}, {m}, {s}))"
            })

        elif conv_type == "hms_to_deg":
            h = int(qs.get("h", 0))
            m = int(qs.get("m", 0))
            s = float(qs.get("s", 0))
            # hms_to_degrees takes an HMS object
            hms = astronomy_types.HMS(h, m, s)
            res = astronomy_types.hms_to_degrees(hms)
            return json_response({
                "result": float(res),
                "call": f"hms_to_degrees(HMS({h}, {m}, {s}))"
            })

        else:
            return json_response({"error": "Unknown conversion type"}, status=400)

    except (ValueError, TypeError) as e:
        return json_response({"error": f"Invalid input parameters: {str(e)}"}, status=400)
    except Exception as e:
        return json_response({"error": str(e), "trace": traceback.format_exc()}, status=500)

async def on_fetch(request, env):
    from urllib.parse import urlparse
    url = str(request.url)
    qs = parse_qs(url)
    path = urlparse(url).path

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    elif path == "/api/info":
        return await handle_info()

    elif path == "/api/convert":
        return await handle_convert(qs)

    elif path == "/style.css":
        headers = Headers.new({"Content-Type": "text/css; charset=utf-8"}.items())
        return Response.new(STYLE_CSS, headers=headers)

    elif path == "/":
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(INDEX_HTML, headers=headers)

    return Response.new("Not Found", status=404)
