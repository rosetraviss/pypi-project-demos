# asyncio-extensions Cloudflare Python Worker Demo

This is a demonstration of the real `asyncio-extensions` PyPI package running inside a Cloudflare Python Worker.

## Live Demo
For documentation and library packages, see: [pypi.rosetraviss.uk/asyncio-extensions](https://pypi.rosetraviss.uk/asyncio-extensions)

## Features
- Interactive web interface demonstrating `LimitedTaskGroup`.
- Simulated background task execution using asynchronous constraints and limits.

## API Endpoints

### `GET /api/run`
Runs a suite of simulated tasks to demonstrate concurrency limits.

**Parameters:**
- `tasks` (integer): Total number of tasks to run.
- `limit` (integer): Concurrency limit for the `LimitedTaskGroup`.

**Example Request:**
```bash
curl "https://asyncio-extensions-demo.<your-subdomain>.workers.dev/api/run?tasks=10&limit=3"
```

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
