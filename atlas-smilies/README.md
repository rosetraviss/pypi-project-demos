# atlas-smilies Cloudflare Python Worker Demo

This is a demonstration of the `atlas-smilies` PyPI package running inside a Cloudflare Python Worker (via Pyodide/WASM).

## Live Demo
The demo is hosted at: [atlas-smilies.pypi.rosetraviss.uk](https://atlas-smilies.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/atlas-smilies](https://pypi.rosetraviss.uk/atlas-smilies)

## Features
- Interactive web interface for exploring the atlas-smilies library.
- Demonstrates how to handle C-extension limitations gracefully in Cloudflare Workers using Pyodide.

## API Endpoints

### `GET /api/info`
Returns general metadata about the atlas-smilies package.

### `GET /api/trajectory`
Simulates or performs multi-omic trajectory inference (depending on worker capabilities).

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
