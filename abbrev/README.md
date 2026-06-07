# abbrev Cloudflare Python Worker Demo

This is a demonstration of the pure-Python `abbrev` library running on Cloudflare Workers (via Pyodide).

## Live Demo
The demo is hosted at: [abbrev.pypi.rosetraviss.uk](https://abbrev.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/abbrev](https://pypi.rosetraviss.uk/abbrev)

## Features
- Real-time generation of shortest unique abbreviations for lists of words.
- Detailed interactive lookup sandbox demonstrating standard `abbrev()` logic.
- REST API endpoint for easy integration into external tooling/CLIs.

## API Endpoint
### `POST /api/abbrev`
Accepts a JSON payload with a list of words and an optional query.

**Example Request:**
```bash
curl -X POST https://abbrev.pypi.rosetraviss.uk/api/abbrev \
  -H "Content-Type: application/json" \
  -d '{"words": ["status", "start", "stop"]}'
```

**Example Response:**
```json
{
  "shortest_mapping": {
    "start": "star",
    "status": "stat",
    "stop": "sto"
  },
  "full_mapping": {
    "sta": "start",
    "star": "start",
    "start": "start",
    "sto": "stop",
    "stop": "stop"
  }
}
```

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
