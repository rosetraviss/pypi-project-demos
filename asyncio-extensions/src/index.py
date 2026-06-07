import json
import asyncio
import sys
import os

# Add python_modules to path so we can import asyncio_extensions
sys.path.insert(0, "./python_modules")
import asyncio_extensions

from js import Response, Headers

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>asyncio-extensions Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f9fafb;
            color: #111827;
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        main {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            max-width: 800px;
            width: 100%;
        }
        h1 { margin-top: 0; color: #2563eb; }
        .demo-section {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #f3f4f6;
            border-radius: 6px;
            transition: transform 0.2s ease-in-out;
        }
        .demo-section:hover {
            transform: scale(1.02);
        }
        button {
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.2s;
        }
        button:hover { background-color: #1d4ed8; }
        button:disabled { background-color: #93c5fd; cursor: not-allowed; }
        #result {
            margin-top: 1rem;
            font-family: monospace;
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 4px;
            white-space: pre-wrap;
            min-height: 50px;
        }
        footer {
            margin-top: auto;
            padding-top: 2rem;
            text-align: center;
            font-size: 0.875rem;
            color: #6b7280;
        }
        footer a { color: #2563eb; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            vertical-align: middle;
            margin-left: 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <main>
        <h1>asyncio-extensions Demo</h1>
        <p>This Cloudflare Python Worker demonstrates the capabilities of the <code>asyncio-extensions</code> package.</p>

        <div class="demo-section">
            <h3>LimitedTaskGroup Demonstration</h3>
            <p>Run multiple simulated tasks with a strict concurrency limit.</p>
            <div>
                <label for="taskCount">Total Tasks:</label>
                <input type="number" id="taskCount" value="10" min="1" max="50" style="width: 60px;">
                <label for="concurrencyLimit" style="margin-left: 10px;">Concurrency Limit:</label>
                <input type="number" id="concurrencyLimit" value="3" min="1" max="10" style="width: 60px;">
            </div>
            <br>
            <button id="runDemoBtn">Run Demo</button>
            <div id="result">Waiting for input...</div>
        </div>
    </main>

    <footer>
        <p>Powered by Cloudflare Python Workers.</p>
        <p>
            Demo provided by <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a> |
            Package: <a href="https://pypi.rosetraviss.uk/asyncio-extensions" target="_blank">asyncio-extensions</a>
        </p>
    </footer>

    <script>
        document.getElementById('runDemoBtn').addEventListener('click', async () => {
            const btn = document.getElementById('runDemoBtn');
            const resultDiv = document.getElementById('result');
            const tasks = document.getElementById('taskCount').value;
            const limit = document.getElementById('concurrencyLimit').value;

            btn.disabled = true;
            btn.innerHTML = 'Running... <span class="loading"></span>';
            resultDiv.textContent = 'Processing tasks...';

            try {
                const response = await fetch(`/api/run?tasks=${tasks}&limit=${limit}`);
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                resultDiv.textContent = `Error: ${err.message}`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Run Demo';
            }
        });
    </script>
</body>
</html>
"""

async def simulate_task(task_id: int):
    # Simulate an I/O operation
    await asyncio.sleep(0.5)
    return f"Task {task_id} completed successfully"

async def run_limited_tasks(total_tasks: int, concurrency_limit: int):
    results = []
    # Use LimitedTaskGroup to run tasks concurrently but cap at concurrency_limit
    async with asyncio_extensions.LimitedTaskGroup(concurrency_limit) as tg:
        tasks = []
        for i in range(total_tasks):
            task = tg.create_task(simulate_task(i))
            tasks.append(task)

    for task in tasks:
        results.append(task.result())

    return results

async def on_fetch(request, env):
    url = request.url

    if url.endswith("/favicon.ico"):
        headers = Headers.new([("Content-Type", "image/gif")])
        favicon_data = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c000000000100010000020144003b")
        return Response.new(favicon_data, headers=headers)

    if "/api/run" in url:
        try:
            # Parse query parameters manually
            query_string = url.split("?")[1] if "?" in url else ""
            params = dict(qs.split("=") for qs in query_string.split("&") if "=" in qs)

            total_tasks = int(params.get("tasks", 5))
            concurrency_limit = int(params.get("limit", 2))

            total_tasks = min(total_tasks, 50)
            concurrency_limit = min(concurrency_limit, 10)

            start_time = asyncio.get_running_loop().time()
            results = await run_limited_tasks(total_tasks, concurrency_limit)
            end_time = asyncio.get_running_loop().time()

            response_data = {
                "status": "success",
                "message": f"Successfully ran {total_tasks} tasks with a concurrency limit of {concurrency_limit}.",
                "duration_seconds": round(end_time - start_time, 2),
                "expected_duration_seconds": round((total_tasks / concurrency_limit) * 0.5, 2),
                "sample_results": results[:3] + ["..."] if len(results) > 3 else results,
                "total_completed": len(results)
            }

            headers = Headers.new([("Content-Type", "application/json")])
            return Response.new(json.dumps(response_data), headers=headers)

        except Exception as e:
            headers = Headers.new([("Content-Type", "application/json")])
            return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)

    # Return the HTML interface
    headers = Headers.new([("Content-Type", "text/html; charset=utf-8")])
    return Response.new(HTML_CONTENT, headers=headers)
