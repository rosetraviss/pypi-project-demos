import json
# pyrefly: ignore [missing-import]
from js import Response, Headers
import abbrev

# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🐜</text></svg>"""


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)


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


def calculate_shortest_abbrevs(words):
    """Calculate the shortest unique abbreviation for each word using the abbrev library."""
    mapping = {}
    unique_words = sorted(list(set(words)))
    for w in unique_words:
        if not w:
            continue
        # Find shortest prefix that uniquely resolves to `w`
        for i in range(1, len(w) + 1):
            prefix = w[:i]
            try:
                resolved = abbrev.abbrev(unique_words, prefix)
                if resolved == w:
                    mapping[w] = prefix
                    break
            except KeyError:
                # Ambiguous or no match
                continue
    return mapping


def calculate_full_abbrevs_map(words):
    """Calculate the full map of all possible unique abbreviations to their original words."""
    mapping = {}
    unique_words = sorted(list(set(words)))
    # For every word, check all prefixes
    for w in unique_words:
        if not w:
            continue
        for i in range(1, len(w) + 1):
            prefix = w[:i]
            try:
                resolved = abbrev.abbrev(unique_words, prefix)
                mapping[prefix] = resolved
            except KeyError:
                continue
    return mapping


# ─────────────────────────────────────────────────────────────────────────────
# HTML UI
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abbrev Demo · Cloudflare Python Worker</title>
  <meta name="description" content="Calculate and visualize shortest unique abbreviations for lists of words, powered by the pure-Python abbrev package on Cloudflare Workers.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:        #06080c;
      --surface:   #0b0f17;
      --surface2:  #111724;
      --border:    rgba(255, 255, 255, 0.08);
      --accent:    #a855f7; /* Purple */
      --accent-rgb: 168, 85, 247;
      --accent2:   #ec4899; /* Pink */
      --accent2-rgb: 236, 72, 153;
      --green:     #10b981;
      --red:       #ef4444;
      --text:      #f3f4f6;
      --muted:     #9ca3af;
      --radius:    16px;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

    /* ── Ambient Orbs ── */
    .orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
    .orb  { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.15; }
    .orb-1 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(var(--accent-rgb), 0.6), transparent 70%); top: -200px; left: -100px; animation: float 18s ease-in-out infinite alternate; }
    .orb-2 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(var(--accent2-rgb), 0.6), transparent 70%); bottom: -150px; right: -50px; animation: float 22s ease-in-out infinite alternate-reverse; }
    @keyframes float { from { transform: translate(0,0) scale(1); } to { transform: translate(30px,40px) scale(1.1); } }

    /* ── Layout ── */
    .container { position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
    
    /* ── Header ── */
    header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 40px; }
    .brand { display: flex; align-items: center; gap: 12px; }
    .logo { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 24px; letter-spacing: -0.02em; }
    .badges { display: flex; gap: 8px; }
    .badge { border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .badge-cf { background: rgba(var(--accent-rgb), 0.15); border: 1px solid rgba(var(--accent-rgb), 0.3); color: var(--accent); }
    .badge-pypi { background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--muted); text-decoration: none; transition: all 0.2s; }
    .badge-pypi:hover { border-color: var(--accent2); color: var(--accent2); }

    /* ── Hero ── */
    .hero { text-align: center; margin-bottom: 48px; }
    h1 { font-size: clamp(32px, 5vw, 64px); font-weight: 800; line-height: 1.1; letter-spacing: -0.03em; margin-bottom: 16px; }
    h1 span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { font-size: 18px; color: var(--muted); max-width: 680px; margin: 0 auto; line-height: 1.6; }
    .hero-sub code { font-family: 'JetBrains Mono', monospace; color: var(--accent); font-size: 0.9em; background: rgba(255,255,255,0.03); padding: 2px 6px; border-radius: 4px; }

    /* ── Grid Layout ── */
    .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
    @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

    /* ── Card Styles ── */
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden; }
    .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2)); opacity: 0.8; }
    .card-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .card-desc { font-size: 14px; color: var(--muted); margin-bottom: 20px; line-height: 1.5; }

    /* ── Inputs & Forms ── */
    label { display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin-bottom: 8px; }
    textarea, input[type="text"] { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; color: var(--text); font-family: 'Outfit', sans-serif; font-size: 15px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
    textarea:focus, input[type="text"]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.15); }
    textarea { resize: vertical; min-height: 120px; font-family: 'JetBrains Mono', monospace; font-size: 14px; }

    /* ── Shortest Abbrevs Results ── */
    .word-list { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }
    .word-item { display: flex; align-items: center; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 16px; justify-content: space-between; }
    .orig-word { font-weight: 600; font-size: 15px; }
    .abbrev-tag { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 13px; color: var(--green); background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 4px 10px; border-radius: 6px; }
    .abbrev-highlight { color: var(--accent2); text-decoration: underline; text-underline-offset: 4px; }

    /* ── Playback Sandbox ── */
    .sandbox-result { margin-top: 16px; padding: 16px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 14px; border: 1px solid var(--border); background: var(--surface2); }
    .result-success { border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.03); color: var(--green); }
    .result-ambiguous { border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.03); color: var(--red); }
    .result-error { border-color: var(--border); background: var(--surface2); color: var(--muted); }

    /* ── API Documentation Panel ── */
    .api-section { margin-top: 40px; }
    pre { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 18px; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.6; overflow-x: auto; color: #e5e7eb; }
    .kw { color: #f472b6; }
    .st { color: #34d399; }
    .nm { color: #fb923c; }
    .cm { color: #6b7280; font-style: italic; }

    /* ── Navigation Tabs ── */
    .tabs { display: flex; gap: 8px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    .tab-btn { background: none; border: none; color: var(--muted); font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 600; padding: 8px 16px; cursor: pointer; border-radius: 6px; transition: all 0.2s; }
    .tab-btn:hover { color: var(--text); background: rgba(255,255,255,0.03); }
    .tab-btn.active { color: var(--text); background: rgba(var(--accent-rgb), 0.15); border: 1px solid rgba(var(--accent-rgb), 0.3); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    /* ── Footer ── */
    footer { text-align: center; margin-top: 60px; padding-top: 24px; border-top: 1px solid var(--border); color: var(--muted); font-size: 14px; }
    footer a { color: var(--accent); text-decoration: none; font-weight: 600; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
  </div>

  <div class="container">
    <header>
      <div class="brand">
        <div class="logo">🐜 abbrev</div>
      </div>
      <div class="badges">
        <span class="badge badge-cf">⚡ Cloudflare Python Worker</span>
        <a href="https://pypi.rosetraviss.uk/abbrev" target="_blank" class="badge badge-pypi">📦 abbrev v1.4.0</a>
      </div>
    </header>

    <section class="hero">
      <h1>Shortest Unique <span>Abbreviations</span></h1>
      <p class="hero-sub">
        Calculate the minimal unique prefix mappings for CLI options, commands, or routes. Powered by the pure-Python <code>abbrev</code> library running globally at the edge.
      </p>
    </section>

    <main class="main-grid">
      <!-- Input Panel -->
      <div class="card">
        <h2 class="card-title">🔌 Configuration Input</h2>
        <p class="card-desc">Enter a list of commands, strings, or flags (one per line). The abbreviations will update in real-time as you type.</p>
        
        <label for="words-input">Words / Flags list</label>
        <textarea id="words-input" placeholder="status&#10;start&#10;stop&#10;restart&#10;resume" spellcheck="false">status
start
stop
restart
resume</textarea>
      </div>

      <!-- Output Panel -->
      <div class="card">
        <div class="tabs">
          <button class="tab-btn active" onclick="switchTab('tab-shortest')">Shortest Mapping</button>
          <button class="tab-btn" onclick="switchTab('tab-full')">Full Abbrev Dict</button>
          <button class="tab-btn" onclick="switchTab('tab-sandbox')">Interactive Sandbox</button>
        </div>

        <!-- Shortest Mapping Tab -->
        <div class="tab-content active" id="tab-shortest">
          <p class="card-desc">The minimal unique abbreviation calculated for each word using <code>abbrev</code> logic.</p>
          <div class="word-list" id="shortest-list">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Full Abbrev Dict Tab -->
        <div class="tab-content" id="tab-full">
          <p class="card-desc">The complete mapping of every valid abbreviation string to its fully resolved target.</p>
          <div class="word-list" id="full-list" style="max-height: 350px; overflow-y: auto;">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Sandbox Tab -->
        <div class="tab-content" id="tab-sandbox">
          <p class="card-desc">Query abbreviations dynamically. Test how ambiguous queries raise KeyErrors or how flags change lookup behavior.</p>
          
          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div>
              <label for="query-input">Search / Abbreviator Query</label>
              <input type="text" id="query-input" placeholder="e.g. sta" value="sta">
            </div>

            <div style="display: flex; gap: 16px;">
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="param-multi"> <code>multi=True</code> (returns all matches)
              </label>
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="param-unique" checked> <code>unique=True</code> (strict checking)
              </label>
            </div>

            <div class="sandbox-result" id="sandbox-output">
              Enter a query to run lookup...
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- API Docs -->
    <section class="api-section">
      <div class="card">
        <h2 class="card-title">📖 Edge API Endpoint Usage</h2>
        <p class="card-desc">Deploy this as a microservice on your edge framework to resolve abbreviations instantly in command line tools or routing systems.</p>
        
        <h3 style="font-size: 14px; font-weight: 700; margin-bottom: 8px;">POST /api/abbrev</h3>
        <pre><span class="cm"># Request Body: JSON list of strings</span>
curl -X POST https://your-worker.workers.dev/api/abbrev \
  -H <span class="st">"Content-Type: application/json"</span> \
  -d <span class="st">'{"words": ["status", "start", "stop"]}'</span>

<span class="cm"># Response Payload</span>
{
  <span class="kw">"shortest_mapping"</span>: {
    <span class="kw">"start"</span>: <span class="st">"star"</span>,
    <span class="kw">"status"</span>: <span class="st">"stat"</span>,
    <span class="kw">"stop"</span>: <span class="st">"sto"</span>
  },
  <span class="kw">"full_mapping"</span>: {
    <span class="kw">"sta"</span>: <span class="st">"start"</span>,
    <span class="kw">"star"</span>: <span class="st">"start"</span>,
    <span class="kw">"start"</span>: <span class="st">"start"</span>,
    <span class="kw">"sto"</span>: <span class="st">"stop"</span>,
    <span class="kw">"stop"</span>: <span class="st">"stop"</span>
  }
}</pre>
      </div>
    </section>

    <footer>
      <p>Powered by the <a href="https://pypi.rosetraviss.uk/abbrev" target="_blank">abbrev</a> library on Cloudflare Python Workers. Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a></p>
    </footer>
  </div>

  <script>
    const wordsInput = document.getElementById('words-input');
    const queryInput = document.getElementById('query-input');
    const paramMulti = document.getElementById('param-multi');
    const paramUnique = document.getElementById('param-unique');
    
    async function updateData() {
      const words = wordsInput.value.split('\n')
        .map(w => w.trim())
        .filter(w => w.length > 0);
      
      const query = queryInput.value.trim();
      const multi = paramMulti.checked;
      const unique = paramUnique.checked;

      if (words.length === 0) {
        document.getElementById('shortest-list').innerHTML = '<div style="color: var(--muted); text-align: center; padding: 20px;">No words entered yet.</div>';
        document.getElementById('full-list').innerHTML = '<div style="color: var(--muted); text-align: center; padding: 20px;">No abbreviations generated.</div>';
        return;
      }

      try {
        const response = await fetch('/api/abbrev', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ words, query, multi, unique })
        });
        const data = await response.json();

        // Render Shortest Mappings
        const shortestHtml = Object.entries(data.shortest_mapping).map(([word, abbrev]) => {
          // Highlight abbreviation inside original word
          const hlStart = word.indexOf(abbrev);
          let highlightedWord = word;
          if (hlStart !== -1) {
            highlightedWord = word.substring(0, hlStart) + 
              '<span class="abbrev-highlight">' + abbrev + '</span>' + 
              word.substring(hlStart + abbrev.length);
          }
          return `
            <div class="word-item">
              <span class="orig-word">${highlightedWord}</span>
              <span class="abbrev-tag">${abbrev}</span>
            </div>
          `;
        }).join('');
        document.getElementById('shortest-list').innerHTML = shortestHtml;

        // Render Full Abbrev Mapping
        const fullHtml = Object.entries(data.full_mapping).map(([abbrev, word]) => `
          <div class="word-item">
            <span class="orig-word" style="font-family: 'JetBrains Mono', monospace; font-size:14px; font-weight: 500;">${abbrev}</span>
            <span class="abbrev-tag" style="background: rgba(168, 85, 247, 0.1); border-color: rgba(168, 85, 247, 0.2); color: var(--accent);">${word}</span>
          </div>
        `).join('');
        document.getElementById('full-list').innerHTML = fullHtml || '<div style="color: var(--muted); text-align: center; padding: 20px;">No mappings.</div>';

        // Render Sandbox Output
        const sandboxOut = document.getElementById('sandbox-output');
        if (!query) {
          sandboxOut.className = 'sandbox-result';
          sandboxOut.textContent = 'Enter a query string above to test the abbreviator lookup.';
        } else if (data.query_error) {
          sandboxOut.className = 'sandbox-result result-ambiguous';
          sandboxOut.innerHTML = `<strong>KeyError:</strong> ${data.query_error}`;
        } else {
          sandboxOut.className = 'sandbox-result result-success';
          sandboxOut.innerHTML = `<strong>Result:</strong> ${JSON.stringify(data.query_result)}`;
        }
      } catch (err) {
        console.error(err);
      }
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
      
      const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.textContent.toLowerCase().includes(tabId.split('-')[1]));
      if (targetBtn) targetBtn.classList.add('active');
      document.getElementById(tabId).classList.add('active');
    }

    wordsInput.addEventListener('input', updateData);
    queryInput.addEventListener('input', updateData);
    paramMulti.addEventListener('change', updateData);
    paramUnique.addEventListener('change', updateData);

    // Initial render
    updateData();
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point / Request Handler
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url = str(request.url)
    path = url.split("?")[0]
    # Normalise path: strip protocol+host
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/abbrev":
        if request.method == "POST":
            try:
                body_text = await request.text()
                body = json.loads(body_text)
                words = body.get("words", [])
                query_key = body.get("query", None)
                multi = body.get("multi", False)
                unique = body.get("unique", True)

                # Calculations
                shortest = calculate_shortest_abbrevs(words)
                full = calculate_full_abbrevs_map(words)

                # Query lookup testing
                query_result = None
                query_error = None
                if query_key:
                    try:
                        query_result = abbrev.abbrev(
                            words,
                            key=query_key,
                            multi=multi,
                            unique=unique
                        )
                    except KeyError as ke:
                        # Convert KeyError to string message
                        query_error = str(ke) if ke.args else f"'{query_key}' is not a valid abbreviation"

                return json_response({
                    "shortest_mapping": shortest,
                    "full_mapping": full,
                    "query_result": query_result,
                    "query_error": query_error
                })
            except Exception as e:
                return json_response({"error": str(e)}, status=400)
        else:
            return json_response({"error": "Method Not Allowed"}, status=405)

    # Return HTML UI for all other paths
    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
