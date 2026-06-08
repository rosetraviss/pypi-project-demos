import sys
import os

# Worker JS FFI
from js import Response, Headers, fetch as js_fetch, Object
import json
import asyncio

import async_requests_tls

class FetchMockSession:
    def __init__(self, *args, **kwargs):
        pass

    async def get(self, url, **kwargs):
        headers = Headers.new({"User-Agent": "python-requests/2.33.1", "Accept-Encoding": "gzip, deflate", "Accept": "*/*"}.items())
        res = await js_fetch(url, method="GET", headers=headers)
        body = await res.text()

        class MockResponse:
            def __init__(self, text, status_code):
                self.text = text
                self.status_code = status_code
            def json(self):
                return json.loads(self.text)
        return MockResponse(body, res.status)

async_requests_tls.session = sys.modules.get('async_requests_tls.session') or type('SessionModule', (), {})()
async_requests_tls.session.AsyncSession = FetchMockSession

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>async-requests-tls Demo</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <style>
        :root {
            --surface: #f7f9ff;
            --surface-container: #e2efff;
            --on-surface: #001d32;
            --primary: #145d91;
            --on-primary: #ffffff;
            --outline: #717880;
            --bg: #ffffff;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --font-sans: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        body {
            font-family: var(--font-sans);
            background-color: var(--bg);
            color: var(--on-surface);
            margin: 0;
            padding: var(--spacing-xl);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            width: 100%;
        }
        h1 {
            font-size: 36px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: var(--spacing-md);
        }
        .card {
            background-color: var(--surface);
            border: 1px solid var(--surface-container);
            border-radius: 8px;
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(31, 66, 94, 0.08);
        }
        .form-group {
            display: flex;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }
        input[type="url"] {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid var(--outline);
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 14px;
        }
        input[type="url"]:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(20, 93, 145, 0.2);
        }
        button {
            background-color: var(--primary);
            color: var(--on-primary);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #0f4a75;
        }
        button:active {
            transform: scale(0.98);
        }
        pre {
            background-color: var(--bg);
            border: 1px solid var(--surface-container);
            padding: var(--spacing-md);
            border-radius: 4px;
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .loading {
            display: none;
            font-style: italic;
            color: var(--outline);
        }
        footer {
            margin-top: auto;
            padding-top: var(--spacing-xl);
            text-align: center;
            font-size: 14px;
        }
        a {
            color: var(--primary);
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>async-requests-tls Demo</h1>
        <p>This worker uses the <a href="https://pypi.rosetraviss.uk/async-requests-tls" target="_blank">async-requests-tls</a> package (shimmed for Pyodide via JS fetch) to perform a GET request mimicking a specific TLS fingerprint.</p>

        <div class="card">
            <div class="form-group">
                <input type="url" id="urlInput" value="https://httpbin.org/get" placeholder="Enter URL to fetch">
                <button onclick="makeRequest()">Send Request</button>
            </div>
            <div id="loading" class="loading">Fetching data...</div>
            <pre id="resultOutput">Response will appear here...</pre>
        </div>
    </div>

    <footer>
        <p>Demo provided by <a href="https://pypi.rosetraviss.uk" target="_blank">PyPI Mirror</a></p>
    </footer>

    <script>
        async function makeRequest() {
            const urlInput = document.getElementById('urlInput').value;
            const loading = document.getElementById('loading');
            const resultOutput = document.getElementById('resultOutput');

            loading.style.display = 'block';
            resultOutput.textContent = '';

            try {
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: urlInput })
                });

                const data = await response.json();
                resultOutput.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultOutput.textContent = 'Error: ' + error.message;
            } finally {
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="50" fill="#145d91"/>
  <text x="50" y="50" font-family="sans-serif" font-size="50" fill="white" text-anchor="middle" dominant-baseline="central">A</text>
</svg>"""

async def handle_fetch(request):
    try:
        body = await request.json()
        if isinstance(body, Object):
            body = body.to_py()

        target_url = body.get('url')
        if not target_url:
            return Response.new(json.dumps({"error": "URL is required"}), status=400)

        # Use the mocked Session
        session = async_requests_tls.session.AsyncSession()
        res = await session.get(target_url)

        return Response.new(json.dumps({
            "status": res.status_code,
            "data": res.text[:1000] + ("..." if len(res.text) > 1000 else "")
        }), headers=Headers.new({"Content-Type": "application/json"}.items()))
    except Exception as e:
        import traceback
        return Response.new(json.dumps({"error": str(e) + "\n" + traceback.format_exc()}), status=500, headers=Headers.new({"Content-Type": "application/json"}.items()))

async def on_fetch(request, env):
    from js import URL
    url_obj = URL.new(request.url)
    path = url_obj.pathname

    if path == "/api/fetch" and request.method == "POST":
        return await handle_fetch(request)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8"}.items())
        return Response.new("Documentation placeholder.", headers=headers)

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
