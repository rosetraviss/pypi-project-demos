# atlaslevels Cloudflare Worker Demo

This project is a Python-based Cloudflare Worker demo for the [atlaslevels](https://pypi.org/project/atlaslevels/) package. It provides an interactive web interface to explore key functionalities like querying atlas ontologies, exploring hierarchy bundles, and verifying metadata.

## Setup

1. Install Cloudflare's `wrangler` CLI and `uv` (the Python package manager).
2. Install the worker's dependencies by running `uv lock` in this directory to generate a cross-platform lockfile.
3. Start the worker locally using `wrangler dev`.

## Features
- **Ontology Explorer:** Query and resolve nodes from the `allen_ccfv3` ontology.
- **Hierarchy Bundle Viewer:** Inspect the hierarchical structure of custom grey matter levels (`allen_gm`).
- **Validation:** Quickly validate preset bundles against ontologies to ensure consistency.

## Environment Note
This runs on Cloudflare Workers using the Pyodide environment. Dependencies are configured natively via `pyproject.toml` and managed by `uv`.

## More Info
- PyPI Page: [atlaslevels](https://pypi.org/project/atlaslevels/)
- User's PyPI mirror: [https://pypi.rosetraviss.uk](https://pypi.rosetraviss.uk)
