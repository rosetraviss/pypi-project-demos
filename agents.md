# Agentic Guidelines for Creating & Maintaining Demo Workers

This document is designed for AI coding assistants (like Antigravity, Jules, and others) that automate, maintain, or update PyPI project demo workers within this repository.

---

## 1. Directory Structure of a Demo Worker

Every demo worker is self-contained in its own root subdirectory (named exactly the PyPI package name, e.g., `abbrev/` or `CurrencyConverter/`).

A standard demo worker contains the following layout:
```text
<package-name>/
├── pyproject.toml       # Defines dependencies (e.g. package, packaging, etc.)
├── uv.lock              # Lockfile managed by uv
├── wrangler.toml        # Cloudflare wrangler configuration
├── README.md            # Demo-specific documentation
└── src/
    └── index.py         # Entrypoint containing the worker handler and UI
```

---

## 2. Cloudflare Python Worker (Pyodide) Limitations & Workarounds

Cloudflare Workers execute Python code using Pyodide compiled to WebAssembly. This environment has specific runtime constraints. When writing or updating `src/index.py`, you **must** apply these workarounds:

### A. Threading is Unsupported
Python libraries that invoke threads or background execution loops will raise runtime errors.
- **Problem**: Libraries like `rich.status` start background threads for loading indicators.
- **Workaround**: Mock the modules/classes before importing the library:
  ```python
  import sys
  from types import ModuleType

  class DummyStatus:
      def __init__(self, *args, **kwargs): pass
      def __enter__(self): return self
      def __exit__(self, *args, **kwargs): pass
      def start(self): pass
      def stop(self): pass
      
  rich_status = ModuleType("rich.status")
  rich_status.Status = DummyStatus
  sys.modules["rich.status"] = rich_status
  ```

### B. Subprocesses are Unsupported
Spawning sub-shells or external binaries will fail because no OS system calls are available in WASM.
- **Problem**: Code calls `subprocess.run()`.
- **Workaround**: Override the subprocess module:
  ```python
  import subprocess
  def mock_run(*args, **kwargs):
      raise FileNotFoundError("Subprocesses are not supported in Emscripten/Pyodide")
  subprocess.run = mock_run
  ```

### C. Network Requests (No Raw Sockets)
Standard Python socket operations and libraries that use them (like standard `urllib` or `requests`) do not function.
- **Problem**: Outbound HTTP requests.
- **Workaround**: Use `pyfetch` from the `pyodide.http` module:
  ```python
  from pyodide.http import pyfetch
  
  response = await pyfetch("https://pypi.org/pypi/requests/json")
  data = await response.json()
  ```

---

## 3. Workflow for Creating a New Demo Worker

When tasked with generating a new demo worker, execute the following steps:

1. **Verify Package Compatibility**:
   - Verify the package is either pure Python or has precompiled Pyodide/WASM support.
   - Look at the wheels on PyPI; if they contain platform-specific C extensions (e.g., `-manylinux_x86_64.whl`) without a pure-python source/wheel counterpart, they will fail to load in the worker.

2. **Initialize Configuration**:
   - Generate `wrangler.toml` with the `python_workers` compatibility flag:
     ```toml
     name = "[package-name]-demo"
     main = "src/index.py"
     compatibility_date = "2024-12-01"
     compatibility_flags = ["python_workers"]
     ```
   - Generate `pyproject.toml` listing the target package under dependencies.

3. **Generate Code (`src/index.py`)**:
   - Write standard Cloudflare Python Worker routing hooks using the `on_fetch(request, env)` signature.
   - Incorporate the single-page HTML interface inside the script to avoid multi-file loading overhead.
   - Adhere strictly to the guidelines in [design.md](file:///c:/Users/rtrav/pypi-project-demos/design.md).

4. **Verify Deployment & Run Locally**:
   - Run `npx wrangler dev` to start a local testing instance and verify endpoint functionality.
