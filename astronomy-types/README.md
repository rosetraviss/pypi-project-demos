# astronomy-types Cloudflare Python Worker Demo

This is a demonstration of the `astronomy-types` PyPI package running inside a Cloudflare Python Worker (via Pyodide/WASM).

## Live Demo
The demo is hosted at: [astronomy-types.pypi.rosetraviss.uk](https://astronomy-types.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/astronomy-types](https://pypi.rosetraviss.uk/astronomy-types)

## Features
- Provides an interactive web UI for performing conversions (e.g. Degrees to Hours, DMS to Degrees, HMS to Degrees).
- Built completely using Cloudflare Python Workers capabilities.
- Live inspection of `astronomy-types` capabilities through `/api/info`.

## API Endpoints

### `GET /api/info`
Returns available functions from the `astronomy-types` package.

### `GET /api/convert`
Performs astronomical conversions.

**Parameters:**
- `type` (string): Conversion type (`deg_to_hrs`, `dms_to_deg`, `hms_to_deg`).
- For `deg_to_hrs`: requires `deg`.
- For `dms_to_deg` and `hms_to_deg`: requires `d`/`h`, `m`, `s`.

**Example Request:**
```bash
curl "https://astronomy-types.pypi.rosetraviss.uk/api/convert?type=deg_to_hrs&deg=180"
```

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
