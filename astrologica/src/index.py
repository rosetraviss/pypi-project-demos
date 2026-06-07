from js import Response, Headers

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>astrologica | Modern Technical Catalog</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --surface: #f7f9ff;
      --surface-container-lowest: #ffffff;
      --surface-container-low: #edf4ff;
      --surface-container: #e2efff;
      --on-surface: #001d32;
      --on-surface-variant: #41474f;
      --primary: #145d91;
      --primary-container: #3776ab;
      --on-primary: #ffffff;
      --secondary: #725c00;
      --secondary-container: #fed33a;
      --on-secondary-container: #715b00;
      --outline: #717880;
      --outline-variant: #c1c7d0;
      --error-container: #ffdad6;
      --on-error-container: #93000a;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', sans-serif;
      background-color: var(--surface);
      color: var(--on-surface);
      margin: 0;
      padding: 32px 16px;
      line-height: 1.5;
      display: flex;
      justify-content: center;
    }

    .container {
      width: 100%;
      max-width: 800px;
      background: var(--surface-container-lowest);
      border: 1px solid var(--outline-variant);
      border-radius: 8px;
      padding: 32px;
      box-shadow: 0 4px 12px rgba(31, 66, 94, 0.04);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .container:hover {
      box-shadow: 0 4px 12px rgba(31, 66, 94, 0.08);
    }

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: var(--primary);
      margin-top: 0;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      letter-spacing: -0.01em;
    }

    .badge {
      font-size: 14px;
      font-family: 'JetBrains Mono', monospace;
      background: var(--surface-container);
      color: var(--on-surface-variant);
      padding: 4px 8px;
      border-radius: 4px;
      font-weight: 400;
    }

    .alert {
      background: var(--error-container);
      color: var(--on-error-container);
      border: 1px solid #ffb4ab;
      padding: 16px;
      border-radius: 4px;
      margin-bottom: 32px;
      font-size: 14px;
    }

    .alert strong {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      font-size: 16px;
    }

    h2 {
      font-size: 20px;
      font-weight: 600;
      margin-top: 32px;
      margin-bottom: 16px;
    }

    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-top: 24px;
      margin-bottom: 12px;
    }

    p {
      font-size: 16px;
      color: var(--on-surface-variant);
      margin-bottom: 16px;
    }

    ul {
      padding-left: 24px;
      color: var(--on-surface-variant);
      margin-bottom: 24px;
    }

    li {
      margin-bottom: 8px;
    }

    code {
      font-family: 'JetBrains Mono', monospace;
      background: var(--surface-container-low);
      color: var(--on-surface);
      padding: 2px 4px;
      border-radius: 4px;
      font-size: 14px;
      border: 1px solid var(--outline-variant);
    }

    footer {
      margin-top: 48px;
      padding-top: 24px;
      border-top: 1px solid var(--outline-variant);
      font-size: 14px;
      display: flex;
      justify-content: space-between;
      color: var(--outline);
    }

    a {
      color: var(--primary-container);
      text-decoration: none;
      font-weight: 600;
    }

    a:hover {
      text-decoration: underline;
    }

    .hero-icon {
      width: 40px;
      height: 40px;
      color: var(--primary);
    }

    .resource-links {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 16px;
      margin-top: 32px;
    }

    .resource-card {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      border: 1px solid var(--outline-variant);
      border-radius: 4px;
      background: var(--surface-container-lowest);
      color: var(--on-surface-variant);
      text-decoration: none;
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      transition: background 0.2s ease, border-color 0.2s ease;
    }

    .resource-card:hover {
      background: var(--surface-container-low);
      border-color: var(--outline);
      text-decoration: none;
    }

    .resource-card svg {
      width: 16px;
      height: 16px;
      stroke: var(--on-surface-variant);
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>
      <svg class="hero-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
        <path d="M2 12h20"></path>
      </svg>
      astrologica
      <span class="badge">0.2.0</span>
    </h1>

    <div class="alert">
      <strong>Environment Limitation</strong>
      The <code>astrologica</code> package depends on <code>pyswisseph</code>, which contains a native C extension (the Swiss Ephemeris library). Because Cloudflare Python Workers (via Pyodide) do not currently support native C extensions unless precompiled to WebAssembly, this package cannot be executed interactively in this demo.
    </div>

    <h2>About the Package</h2>
    <p>Astrology calculations library — traditional Hellenistic focus, Swiss Ephemeris backed.</p>

    <h3>Key Features</h3>
    <ul>
      <li>High-precision calculations via Swiss Ephemeris</li>
      <li>Traditional Hellenistic techniques</li>
      <li>Clean, modern Python interface</li>
    </ul>

    <div class="resource-links">
      <a href="https://pypi.org/project/astrologica/" target="_blank" class="resource-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
        PyPI
      </a>
      <a href="https://github.com/milanpredic/astrologica" target="_blank" class="resource-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        GitHub
      </a>
    </div>

    <footer>
      <span>Astrologica Placeholder Demo</span>
      <span>More demos at <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a></span>
    </footer>
  </div>
</body>
</html>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#145d91"/>
  <path d="M50 10C72 10 90 28 90 50C90 72 72 90 50 90C28 90 10 72 10 50C10 28 28 10 50 10ZM50 20C65 20 78 31 80 46H20C22 31 35 20 50 20ZM50 80C35 80 22 69 20 54H80C78 69 65 80 50 80Z" fill="#ffffff"/>
</svg>"""

LLMS_TXT = """# Astrologica Demo

This is a Cloudflare Python Worker demo for the `astrologica` Python package.

⚠️ **Note:** The `astrologica` package depends on `pyswisseph`, which is a Python wrapper around the Swiss Ephemeris C library. Because Pyodide (the engine that runs Cloudflare Python Workers) does not currently support packages with native C extensions unless they have been explicitly compiled for WebAssembly, `astrologica` cannot be directly imported and run in this environment.

For more details on `astrologica`, visit the [PyPI page](https://pypi.org/project/astrologica/).
For more demos, visit [https://pypi.rosetraviss.uk](https://pypi.rosetraviss.uk).
"""

async def on_fetch(request, env):
    url = str(request.url)
    path = url.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
