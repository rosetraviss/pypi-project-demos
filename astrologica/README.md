# Astrologica Demo Worker

This is a Cloudflare Python Worker demo for the `astrologica` Python package.

⚠️ **Note:** The `astrologica` package depends on `pyswisseph`, which is a Python wrapper around the Swiss Ephemeris C library. Because Pyodide (the engine that runs Cloudflare Python Workers) does not currently support packages with native C extensions unless they have been explicitly compiled for WebAssembly, `astrologica` cannot be directly imported and run in this environment.

This directory contains the placeholder configuration and code structure, as requested, to adhere to the project pattern.

## Usage

This worker simply returns an informational message about the environment limitation.

```bash
npx wrangler dev
```

For more details on `astrologica`, visit the [PyPI page](https://pypi.org/project/astrologica/).
For more demos, visit [https://pypi.rosetraviss.uk](https://pypi.rosetraviss.uk).
