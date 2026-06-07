# async-mega.py Demo

This is a demonstration of the `async-mega.py` package running as a Cloudflare Python Worker.

## Usage Limitations
Because the standard `async-mega.py` package relies on `pycryptodome` (which contains C-extensions not supported by the Pyodide runtime in Cloudflare Workers), this demo runs with the `Crypto` module mocked out. It demonstrates how to deploy the core worker and successfully import the pure-python elements of the package, but cryptographic operations will not function.

## Running Locally
You can run this demo locally using `wrangler`:

```sh
cd async-mega.py
npx wrangler dev
```

Navigate to `http://localhost:8787` in your browser to interact with the demo.

## Links
- [Rose's PyPI Mirror](https://pypi.rosetraviss.uk)
- [async-mega-py on PyPI](https://pypi.org/project/async-mega-py/)
