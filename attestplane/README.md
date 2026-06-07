# attestplane Demo

This directory contains a Cloudflare Python Worker demo for the [attestplane](https://pypi.rosetraviss.uk/attestplane) package.

## Features

- Uses Cloudflare Python Workers (Pyodide) to serve a dynamic Python-backed UI.
- Demonstrates usage of `attestplane` to create `EventDraft`s and compute their hashes.
- Includes a live, interactive web UI with micro-animations and package status checking.

## Usage

You can deploy this worker directly using `wrangler`. Make sure you have `python_workers` compatibility flag set in `wrangler.toml`.
