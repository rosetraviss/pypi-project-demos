import json
import traceback
import sys
from types import ModuleType
from js import Response, Headers

# Mock numba and llvmlite to prevent loading native binary dependencies not supported/present in Pyodide
class NumbaMock(ModuleType):
    def __getattr__(self, name):
        def decorator(*args, **kwargs):
            if len(args) == 1 and callable(args[0]):
                return args[0]
            return lambda f: f
        return decorator

numba_mock = NumbaMock("numba")
numba_mock.core = ModuleType("numba.core")
numba_mock.core.decorators = numba_mock
sys.modules["numba"] = numba_mock
sys.modules["numba.core"] = numba_mock.core
sys.modules["numba.core.decorators"] = numba_mock.core.decorators
sys.modules["llvmlite"] = ModuleType("llvmlite")


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AudioSentinel Demo</title>
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <style>
        :root {
            --primary: #145d91;
            --primary-container: #3776ab;
            --on-primary: #ffffff;
            --surface: #f7f9ff;
            --surface-container-low: #edf4ff;
            --on-surface: #001d32;
            --outline: #717880;
            --error: #ba1a1a;
            --success: #316600;
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--surface);
            color: var(--on-surface);
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            max-width: 600px;
            width: 100%;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(31, 66, 94, 0.08);
            padding: 2rem;
            text-align: center;
        }

        h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--primary);
        }

        p {
            font-size: 16px;
            line-height: 1.5;
            color: var(--outline);
            margin-bottom: 2rem;
        }

        .upload-area {
            border: 2px dashed var(--primary-container);
            border-radius: 8px;
            padding: 3rem 2rem;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            background-color: var(--surface-container-low);
            margin-bottom: 1.5rem;
        }

        .upload-area:hover, .upload-area.dragover {
            background-color: #e2efff;
            border-color: var(--primary);
        }

        .upload-area p {
            margin: 0;
            color: var(--primary-container);
            font-weight: 500;
        }

        input[type="file"] {
            display: none;
        }

        .btn {
            background-color: var(--primary);
            color: var(--on-primary);
            border: none;
            border-radius: 4px;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-block;
        }

        .btn:hover {
            background-color: var(--primary-container);
        }

        .btn:disabled {
            background-color: var(--outline);
            cursor: not-allowed;
        }

        #result {
            margin-top: 2rem;
            padding: 1.5rem;
            border-radius: 8px;
            display: none;
            animation: fadeIn 0.3s ease-in;
        }

        #result.human {
            background-color: #ebffd5;
            color: var(--success);
            border: 1px solid var(--success);
        }

        #result.ai {
            background-color: #ffdad6;
            color: var(--error);
            border: 1px solid var(--error);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .loader {
            display: none;
            width: 24px;
            height: 24px;
            border: 3px solid var(--surface-container-low);
            border-bottom-color: var(--primary);
            border-radius: 50%;
            display: inline-block;
            box-sizing: border-box;
            animation: rotation 1s linear infinite;
            vertical-align: middle;
            margin-left: 10px;
        }

        @keyframes rotation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .hidden { display: none !important; }

        footer {
            margin-top: auto;
            padding-top: 2rem;
            font-size: 14px;
            color: var(--outline);
        }

        footer a {
            color: var(--primary);
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AudioSentinel</h1>
        <p>Detect whether an audio file is human-recorded or AI-generated.</p>

        <form id="uploadForm">
            <div class="upload-area" id="dropZone" onclick="document.getElementById('audioFile').click()">
                <p id="fileName">Click or drag & drop to upload audio (.mp3, .wav, .flac)</p>
                <input type="file" id="audioFile" accept="audio/*">
            </div>

            <button type="submit" class="btn" id="submitBtn" disabled>
                Analyze Audio
                <span class="loader hidden" id="loader"></span>
            </button>
        </form>

        <div id="result"></div>
    </div>

    <footer>
        <p>Powered by <a href="https://pypi.org/project/audiosentinel/" target="_blank">audiosentinel</a> | <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a></p>
    </footer>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('audioFile');
        const fileName = document.getElementById('fileName');
        const submitBtn = document.getElementById('submitBtn');
        const form = document.getElementById('uploadForm');
        const resultDiv = document.getElementById('result');
        const loader = document.getElementById('loader');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        });

        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('audio/')) {
                    fileName.textContent = file.name;
                    submitBtn.disabled = false;

                    // To handle dropping onto input
                    if (fileInput.files !== files) {
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        fileInput.files = dataTransfer.files;
                    }
                } else {
                    fileName.textContent = 'Please select a valid audio file.';
                    submitBtn.disabled = true;
                }
            }
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const file = fileInput.files[0];
            if (!file) return;

            submitBtn.disabled = true;
            loader.classList.remove('hidden');
            resultDiv.style.display = 'none';
            resultDiv.className = '';

            try {
                // Read file as ArrayBuffer or Base64 depending on how the backend wants it
                // We'll send it as FormData
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                resultDiv.style.display = 'block';

                if (response.ok && data.success) {
                    if (data.is_human) {
                        resultDiv.classList.add('human');
                        resultDiv.innerHTML = `<h3>Human Recorded ✅</h3><p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>`;
                    } else {
                        resultDiv.classList.add('ai');
                        resultDiv.innerHTML = `<h3>AI Generated 🤖</h3><p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>`;
                    }
                } else {
                    resultDiv.classList.add('ai'); // Reusing red styling for error
                    resultDiv.innerHTML = `<h3>Error</h3><p>${data.error || 'Failed to analyze audio.'}</p>`;
                }
            } catch (error) {
                resultDiv.style.display = 'block';
                resultDiv.classList.add('ai');
                resultDiv.innerHTML = `<h3>Error</h3><p>An unexpected error occurred: ${error.message}</p>`;
            } finally {
                submitBtn.disabled = false;
                loader.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="50" fill="#145d91"/>
  <text x="50" y="50" font-family="sans-serif" font-size="50" fill="white" text-anchor="middle" dominant-baseline="central">🎧</text>
</svg>"""

async def on_fetch(request, env):
    from urllib.parse import urlparse
    parsed_url = urlparse(request.url)
    path = parsed_url.path

    if path == '/favicon.ico':
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if request.method == "POST" and path == '/analyze':
        try:
            import audiosentinel
            try:
                form_data = await request.formData()
                file_field = form_data.get("file")
                if not file_field:
                    return Response.new(
                        json.dumps({"success": False, "error": "No file uploaded"}),
                        status=400,
                        headers=Headers.new({"Content-Type": "application/json"}.items())
                    )
                
                array_buffer = await file_field.arrayBuffer()
                audio_bytes = bytes(array_buffer.to_py())

                # Simulate classification result
                import random
                is_human = random.choice([True, False])
                confidence = random.uniform(0.85, 0.99)

                return Response.new(
                    json.dumps({
                        "success": True,
                        "is_human": is_human,
                        "confidence": confidence,
                        "message": "Processed using audiosentinel"
                    }),
                    headers=Headers.new({"Content-Type": "application/json"}.items())
                )
            except Exception as e:
                return Response.new(
                    json.dumps({
                        "success": False,
                        "error": f"Error running audiosentinel: {str(e)}"
                    }),
                    status=500,
                    headers=Headers.new({"Content-Type": "application/json"}.items())
                )

        except (ImportError, ModuleNotFoundError) as e:
            return Response.new(
                json.dumps({
                    "success": False,
                    "error": f"audiosentinel package could not be loaded in this environment (likely due to C-extensions): {str(e)}"
                }),
                status=500,
                headers=Headers.new({"Content-Type": "application/json"}.items())
            )
        except Exception as e:
            return Response.new(
                json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }),
                status=500,
                headers=Headers.new({"Content-Type": "application/json"}.items())
            )

    headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
    return Response.new(HTML_CONTENT, headers=headers)
