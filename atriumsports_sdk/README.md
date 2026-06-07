# atriumsports_sdk Cloudflare Python Worker Demo

This is a demonstration of the `atriumsports_sdk` PyPI package running inside a Cloudflare Python Worker via Pyodide.

## Features
- Successfully circumvents `pydantic_core` C-extension restrictions via mock bridging.
- Gracefully bypasses native sockets requirements.
- Demonstrates initialisation of the `AtriumSports` Python object inside the worker environment.

## Live Demo
The demo is hosted at: [atriumsports_sdk.pypi.rosetraviss.uk](https://atriumsports_sdk.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/atriumsports_sdk](https://pypi.rosetraviss.uk/atriumsports_sdk)

## Local Development
Requires Python 3.12+ and `uv`.

1. Run `uv lock` in this directory to ensure `uv.lock` is created.
2. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
