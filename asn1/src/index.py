from js import Response, Headers
import json
import asn1
import traceback

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">📦</text></svg>"""

LLMS_TXT = """# ASN.1 Demo API

> Live demo API and UI for the `asn1` package on Cloudflare Workers, providing a web interface to encode and decode ASN.1 data types.

## Deployment Details
- **Demo URL**: https://asn1.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/asn1
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoints

### `POST /api/encode`
Encodes a given value into ASN.1 hex representation.

#### Request Body
- `type` (string): The data type to encode (`UTF8String`, `Integer`, `Boolean`).
- `value` (string): The value to encode.

#### Response Body
- `hex` (string): The ASN.1 hex encoded representation.
- `error` (string, optional): Error message if encoding fails.

### `POST /api/decode`
Decodes an ASN.1 hex string into its tag and value.

#### Request Body
- `hex` (string): The hex string to decode.

#### Response Body
- `tag` (string): The decoded ASN.1 tag information.
- `value` (string): The decoded value.
- `error` (string, optional): Error message if decoding fails.
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASN.1 Demo</title>
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <style>
        :root {
            --bg-color: #f4f4f9;
            --text-color: #333;
            --accent-color: #007bff;
            --container-bg: #fff;
            --border-color: #ddd;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        h1 {
            margin-bottom: 5px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }
        .container {
            background: var(--container-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            transition: transform 0.2s;
        }
        .container:hover {
            transform: translateY(-2px);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        select, input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            box-sizing: border-box;
            font-family: inherit;
        }
        textarea {
            resize: vertical;
            height: 100px;
            font-family: monospace;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            background-color: var(--accent-color);
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:active {
            transform: scale(0.98);
        }
        button.secondary {
            background-color: #6c757d;
        }
        button.secondary:hover {
            background-color: #5a6268;
        }
        .result-container {
            margin-top: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 6px;
            word-break: break-all;
            min-height: 50px;
            font-family: monospace;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }
        .result-container.show {
            opacity: 1;
        }
        footer {
            margin-top: auto;
            padding: 20px 0;
            text-align: center;
            font-size: 0.9em;
            color: #777;
        }
        footer a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.2s;
        }
        footer a:hover {
            color: #0056b3;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>ASN.1 Demo</h1>
    <div class="subtitle">Cloudflare Python Worker</div>

    <div class="container">
        <div class="form-group">
            <label for="dataType">Data Type (For Encoding)</label>
            <select id="dataType">
                <option value="UTF8String">UTF8String</option>
                <option value="Integer">Integer</option>
                <option value="Boolean">Boolean</option>
            </select>
        </div>

        <div class="form-group">
            <label for="inputValue">Input Value (String, Int, or true/false)</label>
            <input type="text" id="inputValue" placeholder="Enter value to encode">
        </div>

        <div class="form-group">
            <label for="hexInput">Hex Input (For Decoding)</label>
            <textarea id="hexInput" placeholder="Enter hex string to decode (e.g., 0c0568656c6c6f)"></textarea>
        </div>

        <div class="button-group">
            <button onclick="encode()">Encode</button>
            <button class="secondary" onclick="decode()">Decode</button>
        </div>

        <div id="result" class="result-container"></div>
    </div>

    <footer>
        Hosted on <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a> |
        <a href="https://pypi.org/project/asn1/" target="_blank">asn1 PyPI</a>
    </footer>

    <script>
        function showResult(text, isError = false) {
            const res = document.getElementById('result');
            res.textContent = text;
            res.style.color = isError ? 'red' : '#333';
            res.classList.remove('show');
            // Trigger reflow
            void res.offsetWidth;
            res.classList.add('show');
        }

        async function encode() {
            const dataType = document.getElementById('dataType').value;
            const inputValue = document.getElementById('inputValue').value;

            try {
                const response = await fetch('/api/encode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: dataType, value: inputValue })
                });
                const data = await response.json();

                if (data.error) {
                    showResult(`Error: ${data.error}`, true);
                } else {
                    showResult(`Encoded Hex: ${data.hex}`);
                    document.getElementById('hexInput').value = data.hex;
                }
            } catch (err) {
                showResult(`Error: ${err.message}`, true);
            }
        }

        async function decode() {
            const hexInput = document.getElementById('hexInput').value.trim();
            if (!hexInput) {
                showResult('Please enter hex string to decode', true);
                return;
            }

            try {
                const response = await fetch('/api/decode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ hex: hexInput })
                });
                const data = await response.json();

                if (data.error) {
                    showResult(`Error: ${data.error}`, true);
                } else {
                    showResult(`Decoded Tag: ${data.tag}\\nDecoded Value: ${data.value}`);
                }
            } catch (err) {
                showResult(`Error: ${err.message}`, true);
            }
        }
    </script>
</body>
</html>
"""

def handle_encode(request_data):
    try:
        data_type = request_data.get('type')
        value = request_data.get('value')

        encoder = asn1.Encoder()
        encoder.start()

        if data_type == 'UTF8String':
            encoder.write(str(value), asn1.Numbers.UTF8String)
        elif data_type == 'Integer':
            encoder.write(int(value), asn1.Numbers.Integer)
        elif data_type == 'Boolean':
            val = str(value).lower() in ['true', '1', 'yes']
            encoder.write(val, asn1.Numbers.Boolean)
        else:
            return {"error": f"Unsupported type: {data_type}"}

        encoded = encoder.output()
        return {"hex": encoded.hex()}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def handle_decode(request_data):
    try:
        hex_str = request_data.get('hex', '')
        if not hex_str:
            return {"error": "Empty hex input"}

        try:
            encoded_bytes = bytes.fromhex(hex_str)
        except ValueError:
            return {"error": "Invalid hex string"}

        decoder = asn1.Decoder()
        decoder.start(encoded_bytes)

        tag, value = decoder.read()

        tag_info = f"Class: {tag.cls.name}, Type: {tag.typ.name}, Number: {tag.nr.name if hasattr(tag.nr, 'name') else tag.nr}"

        # Handle bytes output for display
        if isinstance(value, bytes):
            value_display = value.hex()
        else:
            value_display = str(value)

        return {
            "tag": tag_info,
            "value": value_display
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def to_js_headers(d):
    # Create a js.Headers object safely using set
    h = Headers.new()
    for k, v in d.items():
        h.set(k, v)
    return h

async def on_fetch(request, env=None):
    url_str = str(request.url)
    path = url_str.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    method = request.method

    headers = to_js_headers({"content-type": "application/json", "Access-Control-Allow-Origin": "*"})
    html_headers = to_js_headers({"content-type": "text/html; charset=utf-8"})
    text_headers = to_js_headers({"content-type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"})
    icon_headers = to_js_headers({"content-type": "image/svg+xml", "Cache-Control": "public, max-age=86400"})

    try:
        if path == "/llms.txt" or path == "/llms-full.txt":
            return Response.new(LLMS_TXT, headers=text_headers)

        if path == "/favicon.ico":
            return Response.new(FAVICON_SVG, headers=icon_headers)

        # Route: GET /
        if method == "GET" and (path == "/" or path == "/index.html"):
            return Response.new(HTML_CONTENT, headers=html_headers)

        # Route: POST /api/encode
        elif method == "POST" and path == "/api/encode":
            req_body = await request.text()
            data = json.loads(req_body) if req_body else {}
            result = handle_encode(data)
            return Response.new(json.dumps(result), headers=headers)

        # Route: POST /api/decode
        elif method == "POST" and path == "/api/decode":
            req_body = await request.text()
            data = json.loads(req_body) if req_body else {}
            result = handle_decode(data)
            return Response.new(json.dumps(result), headers=headers)

        # 404
        else:
            return Response.new(
                json.dumps({"error": "Not Found"}),
                headers=headers,
                status=404
            )
    except Exception as e:
        return Response.new(
            json.dumps({"error": "Internal Server Error", "details": str(e)}),
            headers=headers,
            status=500
        )
