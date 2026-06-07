# assinafy Cloudflare Python Worker Demo

This is a demonstration of the `assinafy` package running as a Cloudflare Python Worker.

## Live Demo
The demo is hosted at: [assinafy.pypi.rosetraviss.uk](https://assinafy.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/assinafy](https://pypi.rosetraviss.uk/assinafy)
Or view the package on PyPI: [pypi.org/project/assinafy/](https://pypi.org/project/assinafy/)

## Features
- Interactive dashboard showcasing `assinafy` features in a Python Cloudflare Worker setup.
- Displays key SDK client resources correctly initialized in a Serverless environment.

## API Endpoint
### `GET /api/info`
Returns general metadata about the running `assinafy` SDK environment, confirming it operates smoothly in a pure Python Pyodide runtime on Cloudflare.

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
