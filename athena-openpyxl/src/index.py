import json
import sys
import os
from js import Response, Headers

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_dir, "python_modules"))

def mock_requests():
    """Mock the requests, requests.adapters, and urllib3 modules using MagicMock to avoid import issues in Pyodide"""
    import sys
    from unittest.mock import MagicMock
    sys.modules['requests'] = MagicMock()
    sys.modules['requests.adapters'] = MagicMock()
    sys.modules['urllib3'] = MagicMock()
    sys.modules['urllib3.util'] = MagicMock()
    sys.modules['urllib3.util.retry'] = MagicMock()

mock_requests()

import openpyxl

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">📊</text></svg>"""

# Unused constants README_MD and LLMS_TXT removed

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>athena-openpyxl Demo</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .demo-section {
            margin-top: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fafafa;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.3s ease;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }
        .btn:hover {
            background: #2980b9;
        }
        pre {
            background: #272822;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .footer a {
            color: #3498db;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .micro-anim {
            transition: transform 0.2s ease-in-out;
        }
        .micro-anim:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>athena-openpyxl Cloudflare Worker Demo</h1>
        <p>This is a demonstration of the <code>athena-openpyxl</code> package running inside a Cloudflare Python Worker.</p>

        <div class="demo-section">
            <h2>API Information</h2>
            <p>Click below to fetch information about the openpyxl package instance running here.</p>
            <button class="btn micro-anim" onclick="fetchInfo()">Get Package Info</button>
            <pre id="info-result">Results will appear here...</pre>
        </div>

        <div class="footer">
            <p>Back to <a href="https://pypi.rosetraviss.uk">pypi.rosetraviss.uk</a> | <a href="https://pypi.rosetraviss.uk/athena-openpyxl">Package Page</a></p>
        </div>
    </div>

    <script>
        async function fetchInfo() {
            const resEl = document.getElementById('info-result');
            resEl.innerText = "Loading...";
            try {
                const response = await fetch('/api/info');
                const data = await response.json();
                resEl.innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                resEl.innerText = "Error fetching info: " + err;
            }
        }
    </script>
</body>
</html>"""

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

async def handle_info():
    try:
        # Just return version and some basic info to prove the package loads
        info = {
            "version": openpyxl.__version__,
            "name": "athena-openpyxl",
            "features": [
                "Workbook",
                "Worksheet",
                "Cell",
                "Styles"
            ]
        }
        return json_response(info)
    except Exception as e:
        print(f"Error in handle_info: {e}")
        import traceback
        traceback.print_exc()
        return json_response({"error": "Internal Server Error"}, status=500)

async def on_fetch(request, env):
    from urllib.parse import urlparse
    parsed_url = urlparse(request.url)
    path = parsed_url.path

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
