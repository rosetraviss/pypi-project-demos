# AtendeAqui Cloudflare Python Worker Demo

This repository contains a demo for the `atendeaqui` Python SDK, specifically designed to run natively on the edge via Cloudflare Python Workers (using Pyodide).

## Live Demo
The demo is available at: [atendeaqui.pypi.rosetraviss.uk](https://atendeaqui.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/atendeaqui](https://pypi.rosetraviss.uk/atendeaqui)

## Architecture Notes
The `atendeaqui` SDK internally relies on `requests`, which requires native sockets. Because Pyodide does not support native sockets, this worker mocks the internal HTTP client (`atendeaqui._http.HttpClient`) to intercept SDK calls and simulate successful interactions with the AtendeAqui API for demonstration purposes.

## Local Development
Requirements:
- Python >= 3.12
- `uv`

1. Install development dependencies:
   ```bash
   uv pip install -r pyproject.toml --extra dev
   ```

2. Run the local development server:
   ```bash
   npx wrangler dev
   ```
