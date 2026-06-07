import json
import ass

# ─────────────────────────────────────────────────────────────────────────────
# Static Assets
# ─────────────────────────────────────────────────────────────────────────────

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎬</text></svg>"""

FOOTER_HTML = """
<footer style="margin-top: 40px; text-align: center; font-size: 14px; color: var(--muted);">
    <p>Powered by <a href="https://pypi.rosetraviss.uk/project/ass-imbk/" target="_blank" style="color: var(--blue);">ass-imbk</a></p>
    <p>Return to <a href="https://pypi.rosetraviss.uk" style="color: var(--blue);">PyPI Mirror</a></p>
</footer>
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ass-imbk Demo · Cloudflare Python Worker</title>
  <meta name="description" content="Live demo of the ass-imbk PyPI package running as a Cloudflare Python Worker.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:        #07090e;
      --surface:   #0d1017;
      --surface2:  #141820;
      --border:    rgba(255,255,255,0.07);
      --accent:    #8b5cf6;
      --accent2:   #6366f1;
      --blue:      #3b82f6;
      --green:     #10b981;
      --text:      #e4e8f0;
      --muted:     #8b949e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: 'Inter', sans-serif;
      background-color: var(--bg); color: var(--text);
      line-height: 1.5; padding-bottom: 60px;
    }}
    .container {{
      max-width: 800px; margin: 0 auto; padding: 40px 20px;
    }}
    header {{
      text-align: center; margin-bottom: 40px;
      animation: fadeInDown 0.6s ease-out;
    }}
    h1 {{
      font-size: 2.5rem; font-weight: 800; margin: 0;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .subtitle {{ color: var(--muted); margin-top: 8px; font-size: 1.1rem; }}
    .panel {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 24px; margin-bottom: 24px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .panel:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.3); }}

    .upload-zone {{
      border: 2px dashed var(--border);
      border-radius: 8px;
      padding: 40px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .upload-zone:hover, .upload-zone.dragover {{
      border-color: var(--accent);
      background: var(--surface2);
    }}
    .upload-zone input[type="file"] {{ display: none; }}

    .btn {{
      display: inline-block; padding: 10px 20px; border-radius: 6px;
      border: none; background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #fff; font-weight: 600; font-family: inherit; cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
      font-size: 1rem;
    }}
    .btn:hover {{ opacity: 0.9; }}
    .btn:active {{ transform: scale(0.98); }}
    .btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

    .result {{ display: none; margin-top: 24px; }}
    .result.show {{ display: block; animation: fadeIn 0.4s ease-out; }}

    .data-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;
    }}
    .data-card {{
      background: var(--surface2); padding: 16px; border-radius: 8px;
      border: 1px solid var(--border);
    }}
    .data-card h3 {{ margin: 0 0 8px 0; font-size: 0.9rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
    .data-card p {{ margin: 0; font-size: 1.25rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }}

    .events-list {{
      margin-top: 24px; max-height: 300px; overflow-y: auto;
      border: 1px solid var(--border); border-radius: 8px; background: var(--surface2);
    }}
    .event-row {{
      padding: 12px 16px; border-bottom: 1px solid var(--border);
      display: flex; gap: 16px;
    }}
    .event-row:last-child {{ border-bottom: none; }}
    .event-time {{ color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; width: 160px; flex-shrink: 0; }}
    .event-text {{ font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

    .error-msg {{ color: #f87171; background: rgba(248,113,113,0.1); padding: 12px; border-radius: 6px; margin-top: 16px; display: none; border: 1px solid rgba(248,113,113,0.2); }}

    @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

    .spinner {{
      display: inline-block; width: 14px; height: 14px; margin-right: 8px;
      border: 2px solid rgba(255,255,255,0.3); border-radius: 50%;
      border-top-color: #fff; animation: spin 1s linear infinite;
      vertical-align: middle;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>ass-imbk Demo</h1>
      <div class="subtitle">Cloudflare Python Worker</div>
    </header>

    <div class="panel">
      <div class="upload-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
        <p style="margin: 0 0 16px 0; font-size: 1.1rem;">Drop an .ass subtitle file here, or click to browse</p>
        <button class="btn" id="upload-btn">Select File</button>
        <input type="file" id="file-input" accept=".ass">
      </div>
      <div class="error-msg" id="error-msg"></div>
    </div>

    <div class="result" id="result-container">
      <h2 style="margin-top: 0;">Parsing Results</h2>
      <div class="data-grid">
        <div class="data-card">
          <h3>Title</h3>
          <p id="res-title">—</p>
        </div>
        <div class="data-card">
          <h3>Resolution</h3>
          <p id="res-res">—</p>
        </div>
        <div class="data-card">
          <h3>Styles</h3>
          <p id="res-styles">—</p>
        </div>
        <div class="data-card">
          <h3>Events</h3>
          <p id="res-events">—</p>
        </div>
      </div>

      <h3 style="margin-top: 32px; margin-bottom: 12px;">Events Preview</h3>
      <div class="events-list" id="events-list">
        <!-- Events populated here -->
      </div>
    </div>

    {FOOTER_HTML}
  </div>

  <script>
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const errorMsg = document.getElementById('error-msg');
    const resultContainer = document.getElementById('result-container');
    const btn = document.getElementById('upload-btn');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {{
      dropZone.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false);
    }});

    function preventDefaults (e) {{ e.preventDefault(); e.stopPropagation(); }}

    ['dragenter', 'dragover'].forEach(eventName => {{
      dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    }});

    ['dragleave', 'drop'].forEach(eventName => {{
      dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    }});

    dropZone.addEventListener('drop', e => {{
      const dt = e.dataTransfer;
      const files = dt.files;
      handleFiles(files);
    }}, false);

    fileInput.addEventListener('change', function() {{
      handleFiles(this.files);
    }});

    function handleFiles(files) {{
      if (files.length === 0) return;
      const file = files[0];
      if (!file.name.endsWith('.ass')) {{
        showError('Please select a valid .ass subtitle file.');
        return;
      }}
      uploadFile(file);
    }}

    function showError(msg) {{
      errorMsg.textContent = msg;
      errorMsg.style.display = 'block';
      resultContainer.classList.remove('show');
    }}

    async function uploadFile(file) {{
      errorMsg.style.display = 'none';
      btn.innerHTML = '<span class="spinner"></span>Parsing...';
      btn.disabled = true;

      try {{
        const text = await file.text();
        const response = await fetch('/api/parse', {{
          method: 'POST',
          body: text
        }});

        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'Failed to parse file');

        document.getElementById('res-title').textContent = data.title || 'Unknown';
        document.getElementById('res-res').textContent = `${{data.play_res_x || '?'}}x${{data.play_res_y || '?'}}`;
        document.getElementById('res-styles').textContent = data.styles_count;
        document.getElementById('res-events').textContent = data.events_count;

        const list = document.getElementById('events-list');
        if (data.events && data.events.length > 0) {{
          const escapeHtml = (unsafe) => {{
            return (unsafe || '').toString()
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
          }};
          list.innerHTML = data.events.map(e =>
            `<div class="event-row">
              <div class="event-time">${{escapeHtml(e.start)}} → ${{escapeHtml(e.end)}}</div>
              <div class="event-text" title="${{escapeHtml(e.text)}}">${{escapeHtml(e.text)}}</div>
            </div>`
          ).join('');
        }} else {{
          list.innerHTML = '<div style="padding: 16px; color: var(--muted); text-align: center;">No events found</div>';
        }}

        resultContainer.classList.add('show');
      }} catch (err) {{
        showError(err.message);
      }} finally {{
        btn.innerHTML = 'Select File';
        btn.disabled = false;
        fileInput.value = '';
      }}
    }}
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# API Helpers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    from js import Headers, Response
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

def text_response(text, content_type="text/plain; charset=utf-8"):
    from js import Headers, Response
    headers = Headers.new({
        "Content-Type": content_type,
        "Access-Control-Allow-Origin": "*"
    }.items())
    return Response.new(text, headers=headers)


# ─────────────────────────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────────────────────────

async def handle_parse(request):
    try:
        content = await request.text()
        if not content:
            return json_response({"error": "Empty body"}, status=400)

        doc = ass.parse_string(content)

        # Extract basic info
        info_dict = dict(doc.info) if hasattr(doc, 'info') else {}
        title = info_dict.get('Title', 'Unknown')
        play_res_x = info_dict.get('PlayResX', '')
        play_res_y = info_dict.get('PlayResY', '')

        styles_count = len(doc.styles) if hasattr(doc, 'styles') else 0
        events_count = len(doc.events) if hasattr(doc, 'events') else 0

        # Get up to 50 events for preview
        events_preview = []
        if hasattr(doc, 'events'):
            for i, ev in enumerate(doc.events):
                if i >= 50:
                    break

                # Format timedelta
                def format_td(td):
                    if not td: return "0:00:00.00"
                    is_negative = td.total_seconds() < 0
                    abs_td = abs(td)
                    total_seconds = int(abs_td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    cents = int(abs_td.microseconds / 10000)
                    sign = "-" if is_negative else ""
                    return f"{sign}{hours}:{minutes:02d}:{seconds:02d}.{cents:02d}"

                start_str = format_td(ev.start) if hasattr(ev, 'start') else ""
                end_str = format_td(ev.end) if hasattr(ev, 'end') else ""

                events_preview.append({
                    "start": start_str,
                    "end": end_str,
                    "text": ev.text if hasattr(ev, 'text') else "",
                    "style": ev.style if hasattr(ev, 'style') else "",
                })

        return json_response({
            "title": title,
            "play_res_x": play_res_x,
            "play_res_y": play_res_y,
            "styles_count": styles_count,
            "events_count": events_count,
            "events": events_preview
        })

    except Exception as e:
        return json_response({"error": f"Failed to parse ASS file: {str(e)}"}, status=400)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    from urllib.parse import urlparse
    path = urlparse(request.url).path or "/"

    method = request.method

    if method == "OPTIONS":
        from js import Headers, Response
        headers = Headers.new({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }.items())
        return Response.new("", headers=headers)

    if path == "/favicon.ico":
        return text_response(FAVICON_SVG, "image/svg+xml")

    if path == "/api/parse" and method == "POST":
        return await handle_parse(request)

    if path == "/":
        from js import Headers, Response
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)

    # Default 404
    from js import Headers, Response
    return Response.new("Not Found", status=404)
