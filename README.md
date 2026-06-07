# PyPI Project Demos

This repository hosts a collection of serverless Cloudflare Workers written in Python (using the Pyodide WebAssembly runtime) that demonstrate various pure-Python PyPI packages.

The primary objective is to show how standard PyPI packages can run natively in edge environments without traditional server setups.

---

## 🗺️ Existing Demos

| Demo / Package | Subdirectory | Description |
| :--- | :--- | :--- |
| **`CurrencyConverter`** | [`CurrencyConverter/`](file:///c:/Users/rtrav/pypi-project-demos/CurrencyConverter) | Real-time currency conversions and rate lookups using ECB data. |
| **`abbrev`** | [`abbrev/`](file:///c:/Users/rtrav/pypi-project-demos/abbrev) | Text abbreviation utility finding the shortest unique mappings for lists of words. |
| **`asn1`** | [`asn1/`](file:///c:/Users/rtrav/pypi-project-demos/asn1) | Interactive encoder and decoder for basic ASN.1 data structures. |
| **`asof`** | [`asof/`](file:///c:/Users/rtrav/pypi-project-demos/asof) | Historical lookup of package releases and versions on PyPI as of a specific date. |
| **`ass-imbk`** | [`ass-imbk/`](file:///c:/Users/rtrav/pypi-project-demos/ass-imbk) | Subtitle parser extracting styles, metadata, and events from `.ass` files. |

---

## 🛠️ Local Development

Each demo runs as a standalone Cloudflare Worker. To run any of them locally:

1. **Prerequisites**: Ensure you have Python 3.12+, `uv` (recommended), and Node.js (for Wrangler CLI) installed.
2. **Navigate** into the specific package directory:
   ```bash
   cd <package-name>
   ```
3. **Run the local dev server**:
   ```bash
   npx wrangler dev
   ```

---

## 📖 Project Documentation

For contributors and automated scripts, see:
- [**Design Guidelines** (`design.md`)](file:///c:/Users/rtrav/pypi-project-demos/design.md): UI styling, palettes, layouts, and footer requirements.
- [**Agent Guidelines** (`agents.md`)](file:///c:/Users/rtrav/pypi-project-demos/agents.md): WebAssembly/Pyodide constraints, mocking rules, and automated code generation instructions.
