"""
aspish Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/aspish/
"""

import json
from js import Response, Headers
import aspish
import aspish.language

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>aspish Demo</title>
  <link rel="icon" href="/favicon.ico">
  <style>
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --border: #e2e8f0;
      --muted: #64748b;
      --radius: 12px;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    body {
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      align-items: center;
    }
    header {
      width: 100%;
      background: var(--card-bg);
      padding: 1.5rem;
      text-align: center;
      border-bottom: 1px solid var(--border);
      box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }
    header h1 { margin: 0; font-size: 1.75rem; color: var(--primary); }
    main {
      flex: 1;
      width: 100%;
      max-width: 800px;
      padding: 2rem 1rem;
      box-sizing: border-box;
    }
    .card {
      background: var(--card-bg);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 2rem;
      margin-bottom: 2rem;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    h2 { margin-top: 0; margin-bottom: 1.5rem; font-size: 1.25rem; }
    .form-row {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      align-items: center;
      animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    input {
      flex: 1;
      padding: 0.75rem 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s;
    }
    input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    button {
      background: var(--primary);
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s, transform 0.1s;
    }
    button:hover { background: var(--primary-hover); }
    button:active { transform: scale(0.98); }
    .btn-secondary {
      background: var(--card-bg);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { background: var(--bg); }
    .btn-danger {
      background: transparent;
      color: #ef4444;
      border: 1px solid #ef4444;
      padding: 0.5rem 1rem;
    }
    .btn-danger:hover { background: #fef2f2; }
    .actions {
      display: flex;
      gap: 1rem;
      margin-top: 1.5rem;
    }
    .spinner {
      display: inline-block;
      width: 1rem;
      height: 1rem;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
      margin-right: 0.5rem;
      vertical-align: middle;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .results {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      min-height: 100px;
    }
    .sibling-pair {
      background: var(--card-bg);
      padding: 0.75rem 1rem;
      border-radius: 6px;
      margin-bottom: 0.5rem;
      border: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      animation: fadeIn 0.3s ease;
    }
    .sibling-pair:last-child { margin-bottom: 0; }
    .error { color: #ef4444; }
    footer {
      width: 100%;
      text-align: center;
      padding: 2rem;
      color: var(--muted);
      border-top: 1px solid var(--border);
      background: var(--card-bg);
    }
    footer a { color: var(--primary); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <h1>aspish Logic Solver</h1>
    <p style="color:var(--muted);margin-top:0.5rem;">Answer Set Programming in Python</p>
  </header>

  <main>
    <div class="card">
      <h2>Family Relationships</h2>
      <p style="color:var(--muted);margin-bottom:1.5rem;">
        Define parent-child facts. The <code>aspish</code> backend will use the rule:
        <br><code>sibling(Y, Z) :- parent(X, Y), parent(X, Z), Y != Z.</code>
      </p>

      <div id="facts-container">
        <!-- Rows will be added here -->
      </div>

      <div class="actions">
        <button type="button" class="btn-secondary" id="add-fact-btn">+ Add Parent Fact</button>
        <button type="button" id="solve-btn">Find Siblings</button>
      </div>
    </div>

    <div class="card">
      <h2>Results</h2>
      <div class="results" id="results-container">
        <p style="color:var(--muted);text-align:center;">Click "Find Siblings" to see results.</p>
      </div>
    </div>
  </main>

  <footer>
    Powered by <a href="https://pypi.org/project/aspish/" target="_blank">aspish</a> |
    <a href="https://pypi.rosetraviss.uk" target="_blank">More packages at pypi.rosetraviss.uk</a>
  </footer>

  <script>
    const factsContainer = document.getElementById('facts-container');
    const addFactBtn = document.getElementById('add-fact-btn');
    const solveBtn = document.getElementById('solve-btn');
    const resultsContainer = document.getElementById('results-container');

    // Initial facts
    const initialFacts = [
      { parent: 'Alice', child: 'Bob' },
      { parent: 'Alice', child: 'Charlie' },
      { parent: 'David', child: 'Eve' },
      { parent: 'David', child: 'Frank' },
    ];

    function createFactRow(parent = '', child = '') {
      const row = document.createElement('div');
      row.className = 'form-row';
      row.innerHTML = `
        <span style="font-family:monospace;color:var(--muted)">parent(</span>
        <input type="text" class="parent-input" placeholder="Parent Name" value="${parent}">
        <span style="font-family:monospace;color:var(--muted)">,</span>
        <input type="text" class="child-input" placeholder="Child Name" value="${child}">
        <span style="font-family:monospace;color:var(--muted)">)</span>
        <button type="button" class="btn-danger remove-btn">×</button>
      `;
      row.querySelector('.remove-btn').addEventListener('click', () => {
        row.remove();
        if (factsContainer.children.length === 0) createFactRow();
      });
      factsContainer.appendChild(row);
    }

    initialFacts.forEach(f => createFactRow(f.parent, f.child));

    addFactBtn.addEventListener('click', () => createFactRow());

    solveBtn.addEventListener('click', async () => {
      const rows = factsContainer.querySelectorAll('.form-row');
      const parents = [];

      rows.forEach(row => {
        const p = row.querySelector('.parent-input').value.trim();
        const c = row.querySelector('.child-input').value.trim();
        if (p && c) {
          parents.push({ name: p, child: c });
        }
      });

      if (parents.length === 0) {
        resultsContainer.innerHTML = '<p class="error">Please enter at least one parent-child relationship.</p>';
        return;
      }

      solveBtn.disabled = true;
      solveBtn.innerHTML = '<span class="spinner"></span>Solving...';
      resultsContainer.innerHTML = '<p style="color:var(--muted);text-align:center;">Solving with aspish...</p>';

      try {
        const response = await fetch('/api/solve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ parents })
        });

        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        if (!data.siblings || data.siblings.length === 0) {
          resultsContainer.innerHTML = '<p style="color:var(--muted);text-align:center;">No siblings found based on the rules.</p>';
        } else {
          resultsContainer.innerHTML = '';
          data.siblings.forEach(s => {
            const div = document.createElement('div');
            div.className = 'sibling-pair';
            div.innerHTML = `
              <span><strong>${s.name1}</strong> and <strong>${s.name2}</strong> are siblings</span>
              <span style="font-family:monospace;color:var(--muted)">sibling(${s.name1}, ${s.name2})</span>
            `;
            resultsContainer.appendChild(div);
          });
        }
      } catch (err) {
        resultsContainer.innerHTML = `<p class="error">Error: ${err.message}</p>`;
      } finally {
        solveBtn.disabled = false;
        solveBtn.innerHTML = 'Find Siblings';
      }
    });
  </script>
</body>
</html>"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#3b82f6"/>
  <text x="50" y="65" font-family="sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">A</text>
</svg>"""

LLMS_TXT = """# aspish Demo

Provides an interactive frontend to input family parent relationships and uses `aspish` to compute siblings.

PyPI: https://pypi.org/project/aspish/
Homepage: https://pypi.rosetraviss.uk"""

LLMS_FULL_TXT = """# aspish Demo Full Info

A demonstration of the `aspish` Python package running within a Cloudflare Worker. Provides an interactive frontend to input family parent relationships and uses `aspish` (ASP - Answer Set Programming) to compute siblings.

PyPI: https://pypi.org/project/aspish/
Homepage: https://pypi.rosetraviss.uk"""

def solve_siblings(parents):
    """
    Given a list of parents dicts [{"name": "Alice", "child": "Bob"}, ...],
    use aspish to compute all siblings.
    Returns a list of dicts [{"name1": "Bob", "name2": "Charlie"}, ...]
    """
    Parent = aspish.predicate("parent", ["name", "child"])
    Sibling = aspish.predicate("sibling", ["name1", "name2"])

    solver = aspish.Solver()

    # Add facts
    for p in parents:
        solver.add(Parent(name=p["name"], child=p["child"]))

    X, Y, Z = aspish.var("X"), aspish.var("Y"), aspish.var("Z")

    # rule: sibling(Y, Z) :- parent(X, Y), parent(X, Z), Y != Z.
    rule = aspish.language.Rule(
        head=Sibling(name1=Y, name2=Z),
        body=(
            Parent(name=X, child=Y),
            Parent(name=X, child=Z),
            Y != Z
        )
    )
    solver.add(rule)
    solver.solve()

    siblings = solver.get(Sibling)
    # Extract values: siblings are Atom objects.
    # We can read their attributes.
    results = []
    for s in siblings:
        results.append({
            "name1": getattr(s, "name1", None),
            "name2": getattr(s, "name2", None),
        })
    return results

async def handle_solve(request):
    try:
        body = await request.json()
        parents = body.get("parents", [])
        siblings = solve_siblings(parents)
        return json_response({"siblings": siblings})
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

async def on_fetch(request, env):
    url = str(request.url)
    path = url.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if request.method == "POST" and path == "/api/solve":
        return await handle_solve(request)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/llms.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        return Response.new(LLMS_FULL_TXT, headers=headers)

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML, headers=headers)
