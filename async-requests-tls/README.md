# async-requests-tls Cloudflare Worker Demo

This is a demonstration of the [`async-requests-tls`](https://pypi.rosetraviss.uk/async-requests-tls) package running on a Cloudflare Worker using the Pyodide WebAssembly environment.

## What is `async-requests-tls`?

`async-requests-tls` is an asynchronous HTTP client in Python that attempts to mimic the TLS fingerprint of standard HTTP requests (such as the `requests` library), making it easier to interface with web services that strictly validate TLS configurations.

## Running Locally

1. `cd async-requests-tls`
2. Ensure you have the necessary dependencies. Note that since Cloudflare Workers run on WebAssembly, pure Python packages or those with WebAssembly wheels are required. You might need `uv` for dependency management.
3. `npm i -g wrangler` (or use `npx wrangler` directly)
4. Run `npx wrangler dev` to start a local testing instance and verify endpoint functionality.

## Documentation

- The user interface design follows the guidelines described in `design.md`.
- Constraints for Pyodide environments are managed per `agents.md`.
