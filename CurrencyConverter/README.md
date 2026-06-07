# CurrencyConverter Cloudflare Python Worker Demo

This is a demonstration of the real `CurrencyConverter` PyPI package running inside a Cloudflare Python Worker (via Pyodide/WASM).

## Live Demo
The demo is hosted at: [CurrencyConverter.pypi.rosetraviss.uk](https://CurrencyConverter.pypi.rosetraviss.uk)

For documentation and library packages, see: [pypi.rosetraviss.uk/CurrencyConverter](https://pypi.rosetraviss.uk/CurrencyConverter)

## Features
- Real-time currency conversion using bundled European Central Bank (ECB) data.
- Live stats extracted directly from the package, showing supported currencies and rates.
- Historical rates lookups (supporting rates from 1999 onwards).
- Support for fallback modes (linear interpolation or last-known rate) and decimal precision modes.

## API Endpoints

### `GET /api/info`
Returns general metadata about the currency converter instance, bounds of rate availability, supported currencies, and exchange rates relative to the Euro.

### `GET /api/convert`
Performs conversion on an amount.

**Parameters:**
- `amount` (float): The amount to convert.
- `from` (string): The 3-letter currency code to convert from (e.g., `USD`).
- `to` (string): The 3-letter currency code to convert to (e.g., `EUR`).
- `date` (string, optional): Date in `YYYY-MM-DD` format to get historical rates.

**Example Request:**
```bash
curl "https://CurrencyConverter.pypi.rosetraviss.uk/api/convert?amount=100&from=USD&to=EUR"
```

## Local Development
Requires Python 3.12+ and `uv`.

1. Run the local dev server using wrangler:
   ```bash
   npx wrangler dev
   ```
