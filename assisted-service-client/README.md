# assisted-service-client Cloudflare Worker Demo

Live demo API and UI for the `assisted-service-client` package on Cloudflare Workers.

## Deployment Details
- **Demo URL**: https://assisted-service-client.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/assisted-service-client
- **Primary Host**: https://pypi.rosetraviss.uk

## What is Demoed
This demo showcases the initialization and usage of the `assisted_service_client.Configuration` class within the Pyodide environment on a Cloudflare Worker. It demonstrates that the library can be successfully imported, and exposes its default properties (such as the default host URL and debug settings) via the interactive UI and API endpoints.

## Development

Install `uv` and `wrangler`. Run:
```bash
uv lock
wrangler dev
```
