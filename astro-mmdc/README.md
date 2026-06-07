# astro-mmdc Cloudflare Python Worker Demo

This is a demonstration of the real `astro-mmdc` PyPI package running inside a Cloudflare Python Worker (via Pyodide/WASM).

## Live Demo
The demo is hosted at: [astro-mmdc.pypi.rosetraviss.uk](https://astro-mmdc.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/astro-mmdc](https://pypi.rosetraviss.uk/astro-mmdc)

## Features
- Query astrophysical databases (cone search).
- Run emission modeling simulations using SSC (Synchrotron Self-Compton) model types.
- Simple, interactive web interface using HTML and CSS with clean styling and micro-animations.

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
