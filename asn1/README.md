# ASN.1 Demo (Cloudflare Python Worker)

This is a demonstration of running the PyPI [`asn1`](https://pypi.org/project/asn1/) package natively within a Cloudflare Worker using Pyodide (Python in WebAssembly).

## Purpose

The main purpose of this repository is to demonstrate how pure-Python packages can be used inside Cloudflare Workers without server infrastructure. It provides a simple UI to encode and decode basic ASN.1 data types (UTF8String, Integer, Boolean) directly in the browser via an API powered by the `asn1` package.

## Setup & Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the local development server:
   ```bash
   npx wrangler dev
   ```

3. Open the provided `localhost` URL in your browser to interact with the UI.

## Structure

- `src/index.py`: The entrypoint for the Cloudflare Worker. Handles routing, rendering the HTML UI, and processing the `/api/encode` and `/api/decode` endpoints.
- `pyproject.toml` / `wrangler.toml`: Configuration files detailing the dependencies (`asn1`) and enabling the `python_workers` compatibility flag.
