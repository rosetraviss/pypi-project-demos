# asof Cloudflare Python Worker Demo

This is a demonstration of the `asof` library running on Cloudflare Workers (via Pyodide).

## Live Demo
The demo is hosted at: [asof.pypi.rosetraviss.uk](https://asof.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/asof](https://pypi.rosetraviss.uk/asof)

## Features
- Interactive web interface to query package versions as of a specific date.
- Real-time generation of information about package versions based on a specific date.
- Clean styling with micro-animations.

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
