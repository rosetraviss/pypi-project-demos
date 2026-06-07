"""
CurrencyConverter Demo — Cloudflare Python Worker
Demonstrates the actual PyPI package: https://pypi.org/project/CurrencyConverter/

Uses: from currency_converter import CurrencyConverter, RateNotFoundError
The package ships with bundled ECB data (no download needed at cold-start).
We also show the SINGLE_DAY_ECB_URL data-source option via a Worker-compatible
fetch shim, since urllib.request is not available in the Workers runtime.
"""

# ── Real CurrencyConverter package imports ────────────────────────────────────
from currency_converter import (
    CurrencyConverter,
    RateNotFoundError,
    SINGLE_DAY_ECB_URL,
    ECB_URL,
)

# ── Workers JS FFI ────────────────────────────────────────────────────────────
from js import Response, Headers, fetch as js_fetch

import json
import io
import zipfile
from datetime import date, datetime

# ─────────────────────────────────────────────────────────────────────────────
# Documentation & Assets
# ─────────────────────────────────────────────────────────────────────────────

LLMS_TXT = """# CurrencyConverter Demo API

> Live demo API and UI for the `CurrencyConverter` package on Cloudflare Workers, providing real-time and historical currency exchange conversions.

## Deployment Details
- **Demo URL**: https://CurrencyConverter.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/CurrencyConverter
- **Primary Host**: https://pypi.rosetraviss.uk

## API Endpoints

### `GET /api/info`
Returns general metadata about the currency converter instance, bounds of rate availability, supported currencies, and exchange rates relative to the Euro.

#### Response Body
- `currencies` (array of strings): List of all supported currency codes (e.g., `USD`, `GBP`).
- `bounds` (array of objects): Earliest and latest data date available for each currency.
- `rates` (array of objects): Map of each currency to its value in EUR.
- `earliest_date` (string): Earliest date with rates.
- `latest_date` (string): Latest date with rates.
- `version` (string): Version of `currency-converter` installed.

---

### `GET /api/convert`
Performs conversion on an amount.

#### Query Parameters
- `amount` (number, required): The amount to convert.
- `from` (string, required): The 3-letter source currency code (e.g., `USD`).
- `to` (string, required): The 3-letter target currency code (e.g., `EUR`).
- `date` (string, optional): Date in `YYYY-MM-DD` format to get historical rates.

#### Response Body
- `amount` (number): Input amount.
- `from` (string): Source currency code.
- `to` (string): Target currency code.
- `result` (number): Converted amount.
- `rate` (number): Conversion rate applied.
- `date` (string): Date of the conversion rate data.
- `call` (string): The Python library call representation.
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">💱</text></svg>"""


# ─────────────────────────────────────────────────────────────────────────────
# Module-level converter (loaded once from bundled ECB data)
# c = CurrencyConverter() uses the CSV bundled inside the wheel — no HTTP needed.
# ─────────────────────────────────────────────────────────────────────────────
_converter: CurrencyConverter | None = None

def get_converter() -> CurrencyConverter:
    global _converter
    if _converter is None:
        # Uses the bundled ECB data that ships with the currency_converter wheel.
        # This is exactly what the library does when you call CurrencyConverter()
        # with no arguments — same as `from currency_converter import CurrencyConverter; c = CurrencyConverter()`
        _converter = CurrencyConverter()
    return _converter


# ─────────────────────────────────────────────────────────────────────────────
# HTML UI
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CurrencyConverter Demo · Cloudflare Python Worker</title>
  <meta name="description" content="Live demo of the CurrencyConverter PyPI package running as a Cloudflare Python Worker, using real European Central Bank data bundled with the package.">
  <link rel="icon" href="/favicon.ico" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:        #07090e;
      --surface:   #0d1017;
      --surface2:  #141820;
      --border:    rgba(255,255,255,0.07);
      --accent:    #f6821f;
      --accent2:   #e84393;
      --blue:      #3b82f6;
      --green:     #10d9a0;
      --text:      #e4e8f0;
      --muted:     #60687a;
      --radius:    14px;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

    /* ── Gradient orbs ── */
    .orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
    .orb  { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.3; }
    .orb-1 { width: 700px; height: 700px; background: radial-gradient(circle, #f6821f66, transparent 65%); top: -250px; left: -150px; animation: drift 20s ease-in-out infinite alternate; }
    .orb-2 { width: 500px; height: 500px; background: radial-gradient(circle, #3b82f655, transparent 65%); bottom: -150px; right: -100px; animation: drift 25s ease-in-out infinite alternate-reverse; }
    .orb-3 { width: 400px; height: 400px; background: radial-gradient(circle, #e8439340, transparent 65%); top: 45%; left: 48%; animation: drift 16s ease-in-out infinite alternate; }
    @keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(40px,50px) scale(1.12); } }

    /* ── Layout ── */
    .container { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 0 24px; }

    /* ── Header ── */
    header { padding: 28px 0 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .badge { border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 700; letter-spacing: 0.04em; }
    .badge-cf  { background: linear-gradient(135deg, #f6821f, #e84393); color: #fff; }
    .badge-pypi { border: 1px solid var(--border); color: var(--muted); text-decoration: none; transition: all .2s; }
    .badge-pypi:hover { border-color: var(--accent); color: var(--accent); }

    /* ── Hero ── */
    .hero { padding: 60px 0 44px; text-align: center; }
    .live-tag { display: inline-flex; align-items: center; gap: 8px; background: rgba(246,130,31,.12); border: 1px solid rgba(246,130,31,.25); border-radius: 999px; padding: 6px 18px; font-size: 13px; color: var(--accent); font-weight: 600; margin-bottom: 24px; }
    .live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); animation: blink 2s ease-in-out infinite; }
    @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.2; } }
    h1 { font-size: clamp(38px, 6.5vw, 76px); font-weight: 800; line-height: 1.04; letter-spacing: -.03em; background: linear-gradient(140deg, #fff 0%, #9aa3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px; }
    h1 span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .hero-sub { font-size: 18px; color: var(--muted); max-width: 600px; margin: 0 auto 20px; line-height: 1.65; }
    .hero-sub code { font-family: 'JetBrains Mono', monospace; color: var(--accent); font-size: .88em; }
    .data-info { font-size: 13px; color: var(--muted); display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; }
    .data-info a { color: var(--blue); text-decoration: none; }
    .data-info a:hover { text-decoration: underline; }
    .data-info strong { color: var(--text); }

    /* ── Main Converter Card ── */
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 12px 48px rgba(0,0,0,.45), 0 0 60px rgba(246,130,31,.08); }
    .card-header { padding: 18px 28px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .card-title { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .09em; }
    .pkg-label { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--muted); }
    .card-body { padding: 28px; }

    /* ── Form ── */
    .conv-grid { display: grid; grid-template-columns: 1fr 44px 1fr; gap: 14px; align-items: end; margin-bottom: 18px; }
    @media (max-width: 580px) { .conv-grid { grid-template-columns: 1fr; } .swap-btn { margin: 0 auto; } }
    label { display: block; font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .07em; margin-bottom: 8px; }
    .input-wrap { display: flex; background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: border-color .2s, box-shadow .2s; }
    .input-wrap:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(246,130,31,.12); }
    .input-wrap input { flex: 1; background: none; border: none; outline: none; color: var(--text); font-size: 21px; font-weight: 700; padding: 14px 16px; font-family: 'JetBrains Mono', monospace; min-width: 0; }
    .input-wrap input::placeholder { color: var(--muted); }
    .cur-sel { background: rgba(255,255,255,.04); border: none; border-left: 1px solid var(--border); color: var(--text); font-size: 14px; font-weight: 700; padding: 0 14px; cursor: pointer; outline: none; min-width: 88px; font-family: 'Inter', sans-serif; }
    .cur-sel option { background: #141820; }
    .swap-btn { width: 44px; height: 44px; background: var(--surface2); border: 1px solid var(--border); border-radius: 50%; color: var(--accent); font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s; align-self: flex-end; }
    .swap-btn:hover { background: rgba(246,130,31,.14); border-color: var(--accent); transform: rotate(180deg) scale(1.1); }
    .result-wrap .input-wrap { border-color: rgba(16,217,160,.2); }
    .result-wrap .input-wrap:focus-within { border-color: var(--green); box-shadow: 0 0 0 3px rgba(16,217,160,.1); }
    .result-wrap input { color: var(--green); }

    .convert-btn { width: 100%; padding: 16px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border: none; border-radius: 10px; color: #fff; font-size: 16px; font-weight: 700; cursor: pointer; transition: all .2s; font-family: 'Inter', sans-serif; letter-spacing: .01em; }
    .convert-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 28px rgba(246,130,31,.35); }
    .convert-btn:active { transform: translateY(0); }
    .convert-btn:disabled { opacity: .5; cursor: not-allowed; transform: none !important; }

    /* ── Result ── */
    .result-panel { margin-top: 18px; background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; display: none; }
    .result-panel.show { display: block; animation: fadeUp .25s ease; }
    @keyframes fadeUp { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
    .result-amount { font-size: 38px; font-weight: 800; font-family: 'JetBrains Mono', monospace; background: linear-gradient(135deg, var(--green), var(--blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .result-meta { font-size: 13px; color: var(--muted); font-family: 'JetBrains Mono', monospace; margin-top: 5px; }
    .result-error { color: #f87171; font-size: 14px; font-weight: 500; }

    /* ── API Demo Cards ── */
    .section { padding-bottom: 64px; }
    .section-label { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; text-align: center; margin-bottom: 24px; }
    .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(308px, 1fr)); gap: 16px; }
    .api-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; transition: all .22s; }
    .api-card:hover { border-color: rgba(246,130,31,.3); transform: translateY(-2px); box-shadow: 0 14px 36px rgba(0,0,0,.35); }
    .api-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 19px; margin-bottom: 14px; }
    .ic-o { background: rgba(246,130,31,.14); }
    .ic-b { background: rgba(59,130,246,.14); }
    .ic-g { background: rgba(16,217,160,.14); }
    .ic-p { background: rgba(232,67,147,.14); }
    .api-title { font-size: 15px; font-weight: 700; margin-bottom: 7px; }
    .api-desc  { font-size: 13px; color: var(--muted); line-height: 1.65; margin-bottom: 16px; }
    pre.code { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 13px 15px; font-family: 'JetBrains Mono', monospace; font-size: 11.5px; line-height: 1.85; overflow-x: auto; white-space: pre; }
    .kw  { color: #f472b6; }
    .fn  { color: #60a5fa; }
    .st  { color: #86efac; }
    .nm  { color: #fb923c; }
    .cm  { color: #4b5563; font-style: italic; }

    /* ── Live API panel ── */
    .live-section { padding-bottom: 64px; }
    .live-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
    .live-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    .live-card-header { padding: 14px 20px; border-bottom: 1px solid var(--border); font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; display: flex; align-items: center; gap: 8px; }
    .live-card-header .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: blink 2s ease-in-out infinite; }
    .live-card-body { padding: 20px; }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .stat { }
    .stat-label { font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }
    .stat-value { font-size: 18px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--green); }
    .stat-value.blue { color: var(--blue); }
    .stat-value.orange { color: var(--accent); }
    .bounds-list { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--muted); line-height: 2; max-height: 200px; overflow-y: auto; }
    .bounds-row span { color: var(--text); font-weight: 600; }

    /* ── Rates Table ── */
    .table-section { padding-bottom: 64px; }
    .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    .table-search { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; gap: 12px; align-items: center; }
    .search-inp { flex: 1; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 9px 14px; color: var(--text); font-size: 14px; outline: none; font-family: 'Inter', sans-serif; transition: border-color .2s; }
    .search-inp:focus { border-color: var(--accent); }
    .count-label { font-size: 12px; color: var(--muted); white-space: nowrap; }
    .table-scroll { max-height: 420px; overflow-y: auto; }
    table { width: 100%; border-collapse: collapse; }
    thead th { position: sticky; top: 0; background: var(--surface2); padding: 11px 18px; font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; text-align: left; border-bottom: 1px solid var(--border); }
    tbody tr:hover { background: rgba(255,255,255,.025); }
    tbody td { padding: 10px 18px; font-size: 13.5px; border-bottom: 1px solid rgba(255,255,255,.04); }
    .cc { font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .rv { font-family: 'JetBrains Mono', monospace; color: var(--green); }
    .ev { font-family: 'JetBrains Mono', monospace; color: var(--blue); }

    /* ── Footer ── */
    footer { border-top: 1px solid var(--border); padding: 30px 0; text-align: center; color: var(--muted); font-size: 13px; margin-bottom: 0; }
    footer a { color: var(--accent); text-decoration: none; }
    footer a:hover { text-decoration: underline; }

    /* ── Spinner / scrollbar ── */
    .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.2); border-top-color: #fff; border-radius: 50%; animation: spin .65s linear infinite; vertical-align: middle; margin-right: 7px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 3px; }
  </style>
</head>
<body>
  <div class="orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>

  <div class="container">
    <header>
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span class="badge badge-cf">⚡ Cloudflare Python Worker</span>
        <a href="https://pypi.rosetraviss.uk/CurrencyConverter" class="badge badge-pypi" target="_blank" rel="noopener">
          📦 pip install CurrencyConverter
        </a>
      </div>
      <div style="font-size:12px;color:var(--muted);font-family:'JetBrains Mono',monospace" id="pkg-version"></div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="live-tag"><div class="live-dot"></div> Live ECB data · Pyodide · Python Worker</div>
      <h1>Currency<span>Converter</span></h1>
      <p class="hero-sub">
        The real <code>CurrencyConverter</code> PyPI package, installed into a Cloudflare
        Python Worker via Pyodide. Powered by
        <a href="https://www.ecb.europa.eu" style="color:var(--accent);text-decoration:none" target="_blank" rel="noopener">ECB</a>
        exchange rate data bundled with the wheel.
      </p>
      <div class="data-info">
        📅 Rate date: <strong id="rate-date">Loading…</strong>
        &nbsp;·&nbsp;
        🌍 <strong id="cur-count">—</strong> currencies
        &nbsp;·&nbsp;
        <a href="https://github.com/alexprengere/currencyconverter" target="_blank" rel="noopener">GitHub ↗</a>
      </div>
    </section>

    <!-- Converter -->
    <section class="section">
      <div class="card">
        <div class="card-header">
          <span class="card-title">c.convert(amount, from_currency, to_currency)</span>
          <span class="pkg-label">currency_converter v<span id="pkg-ver-inline">…</span></span>
        </div>
        <div class="card-body">
          <div class="conv-grid">
            <div>
              <label for="amount-in">Amount</label>
              <div class="input-wrap">
                <input type="number" id="amount-in" value="100" min="0" step="any" placeholder="100">
                <select class="cur-sel" id="from-cur" aria-label="From currency"></select>
              </div>
            </div>
            <button class="swap-btn" id="swap-btn" title="Swap currencies" aria-label="Swap">⇄</button>
            <div class="result-wrap">
              <label for="to-cur">To</label>
              <div class="input-wrap">
                <input type="number" id="result-in" readonly placeholder="—" style="font-size:21px;font-weight:700">
                <select class="cur-sel" id="to-cur" aria-label="To currency"></select>
              </div>
            </div>
          </div>
          <button class="convert-btn" id="conv-btn" onclick="doConvert()">Convert</button>
          <div class="result-panel" id="result-panel">
            <div class="result-amount" id="res-amount"></div>
            <div class="result-meta" id="res-meta"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Live stats from /api/info -->
    <section class="live-section">
      <div class="section-label">📊 Live Package Stats · from <code style="color:var(--accent);font-size:.9em">c.currencies</code> and <code style="color:var(--accent);font-size:.9em">c.bounds</code></div>
      <div class="live-grid">
        <div class="live-card">
          <div class="live-card-header"><div class="dot"></div>CurrencyConverter Instance</div>
          <div class="live-card-body">
            <div class="stat-grid" id="stats-grid">
              <div class="stat"><div class="stat-label">Currencies</div><div class="stat-value" id="stat-currencies">…</div></div>
              <div class="stat"><div class="stat-label">Data Date</div><div class="stat-value blue" id="stat-date">…</div></div>
              <div class="stat"><div class="stat-label">Earliest Date</div><div class="stat-value orange" id="stat-earliest">…</div></div>
              <div class="stat"><div class="stat-label">Latest Date</div><div class="stat-value orange" id="stat-latest">…</div></div>
            </div>
          </div>
        </div>
        <div class="live-card">
          <div class="live-card-header"><div class="dot"></div>Currency Bounds (c.bounds)</div>
          <div class="live-card-body">
            <div class="bounds-list" id="bounds-list"><span class="spinner"></span> Loading…</div>
          </div>
        </div>
        <div class="live-card">
          <div class="live-card-header"><div class="dot"></div>Historical Conversion</div>
          <div class="live-card-body" id="hist-panel">
            <p style="font-size:13px;color:var(--muted);margin-bottom:14px">Convert using <code style="color:var(--accent);font-size:.9em">c.convert(amount, from, to, date=date(year, month, day))</code></p>
            <label for="hist-amount" style="margin-bottom:6px">Amount &amp; currencies</label>
            <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap">
              <input type="number" id="hist-amount" value="100" style="width:90px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:14px;font-family:'JetBrains Mono',monospace;outline:none">
              <select id="hist-from" class="cur-sel" style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;min-width:80px"></select>
              <span style="align-self:center;color:var(--muted)">→</span>
              <select id="hist-to" class="cur-sel" style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;min-width:80px"></select>
            </div>
            <label for="hist-date" style="margin-bottom:6px">Date</label>
            <div style="display:flex;gap:8px;align-items:center">
              <input type="date" id="hist-date" value="2013-03-21" style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:14px;outline:none;font-family:'Inter',sans-serif">
              <button onclick="doHistorical()" style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 16px;color:var(--text);font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all .2s" onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='var(--border)'">Look up ↗</button>
            </div>
            <div id="hist-result" style="margin-top:12px;font-family:'JetBrains Mono',monospace;font-size:14px;color:var(--green);min-height:20px"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- API Code Showcase -->
    <section class="section">
      <div class="section-label">📖 Package API — Code Samples</div>
      <div class="api-grid">
        <div class="api-card">
          <div class="api-icon ic-o">🔄</div>
          <div class="api-title">Basic Conversion</div>
          <div class="api-desc">Core <code style="color:var(--accent);font-size:.9em">convert()</code> method — amount, source currency, target currency. Default target is EUR.</div>
          <pre class="code"><span class="kw">from</span> currency_converter <span class="kw">import</span> CurrencyConverter

c = CurrencyConverter()

<span class="cm"># Convert 100 USD → EUR</span>
c.convert(<span class="nm">100</span>, <span class="st">'USD'</span>, <span class="st">'EUR'</span>)
<span class="cm"># → 91.57 (varies by date)</span>

<span class="cm"># Default target is EUR</span>
c.convert(<span class="nm">100</span>, <span class="st">'GBP'</span>)
<span class="cm"># → 118.3</span></pre>
        </div>

        <div class="api-card">
          <div class="api-icon ic-b">📅</div>
          <div class="api-title">Historical Rates</div>
          <div class="api-desc">Full ECB history since 1999. Pass a <code style="color:var(--accent);font-size:.9em">date=</code> argument to query any past rate.</div>
          <pre class="code"><span class="kw">from</span> datetime <span class="kw">import</span> date

c = CurrencyConverter()

c.convert(<span class="nm">100</span>, <span class="st">'EUR'</span>, <span class="st">'USD'</span>,
          date=date(<span class="nm">2013</span>, <span class="nm">3</span>, <span class="nm">21</span>))
<span class="cm"># → 129.1</span>

c.convert(<span class="nm">100</span>, <span class="st">'GBP'</span>, <span class="st">'EUR'</span>,
          date=date(<span class="nm">2020</span>, <span class="nm">1</span>, <span class="nm">1</span>))
<span class="cm"># → 118.07</span></pre>
        </div>

        <div class="api-card">
          <div class="api-icon ic-g">🌐</div>
          <div class="api-title">Data Sources</div>
          <div class="api-desc">Use bundled data, the full ECB history, single-day ECB data, or your own CSV file in ECB format.</div>
          <pre class="code"><span class="kw">from</span> currency_converter <span class="kw">import</span> (
    ECB_URL, SINGLE_DAY_ECB_URL,
    CurrencyConverter,
)
<span class="cm"># Bundled (fastest, in this worker)</span>
c = CurrencyConverter()

<span class="cm"># Full history — live download</span>
c = CurrencyConverter(ECB_URL)

<span class="cm"># Today only — smallest download</span>
c = CurrencyConverter(SINGLE_DAY_ECB_URL)</pre>
        </div>

        <div class="api-card">
          <div class="api-icon ic-p">🛡️</div>
          <div class="api-title">Fallback Modes</div>
          <div class="api-desc">Handle missing rates via linear interpolation or last-known rate. Handle out-of-bounds dates gracefully.</div>
          <pre class="code"><span class="cm"># Missing rate → interpolate</span>
c = CurrencyConverter(
    fallback_on_missing_rate=<span class="kw">True</span>
)
c.convert(<span class="nm">100</span>, <span class="st">'BGN'</span>,
          date=date(<span class="nm">2010</span>, <span class="nm">11</span>, <span class="nm">21</span>))
<span class="cm"># → 51.12 (linear interpolation)</span>

<span class="cm"># Date before data → use earliest</span>
c = CurrencyConverter(
    fallback_on_wrong_date=<span class="kw">True</span>)
c.convert(<span class="nm">100</span>, <span class="st">'EUR'</span>, <span class="st">'USD'</span>,
          date=date(<span class="nm">1986</span>, <span class="nm">2</span>, <span class="nm">2</span>))</pre>
        </div>

        <div class="api-card">
          <div class="api-icon ic-o">🎯</div>
          <div class="api-title">Currencies & Bounds</div>
          <div class="api-desc">Inspect the full set of supported currencies and the date range of data available for each one.</div>
          <pre class="code"><span class="cm"># Set of all supported currencies</span>
c.currencies
<span class="cm"># → {'USD', 'GBP', 'JPY', ...}</span>

<span class="cm"># First and last available date</span>
first, last = c.bounds[<span class="st">'USD'</span>]
<span class="cm"># first → datetime.date(1999, 1, 4)</span>
<span class="cm"># last  → datetime.date(2024, xx, xx)</span>

<span class="cm"># Guard: check before converting</span>
<span class="kw">if</span> <span class="st">'AAA'</span> <span class="kw">not in</span> c.currencies:
    <span class="kw">raise</span> ValueError(<span class="st">"unsupported"</span>)</pre>
        </div>

        <div class="api-card">
          <div class="api-icon ic-b">🔢</div>
          <div class="api-title">Decimal Precision</div>
          <div class="api-desc">Use Python's <code style="color:var(--accent);font-size:.9em">decimal.Decimal</code> for exact arithmetic — important for financial applications.</div>
          <pre class="code"><span class="kw">from</span> datetime <span class="kw">import</span> date

<span class="cm"># decimal=True slows load ~10x</span>
<span class="cm"># but gives exact arithmetic</span>
c = CurrencyConverter(decimal=<span class="kw">True</span>)

c.convert(<span class="nm">100</span>, <span class="st">'EUR'</span>, <span class="st">'USD'</span>,
          date=date(<span class="nm">2013</span>, <span class="nm">3</span>, <span class="nm">21</span>))
<span class="cm"># → Decimal('129.100')</span>
<span class="cm"># (not 129.09999999... float)</span></pre>
        </div>
      </div>
    </section>

    <!-- Rates Table -->
    <section class="table-section">
      <div class="section-label">💱 All Rates from <code style="color:var(--accent)">c.convert(1, currency, 'EUR')</code></div>
      <div class="table-wrap">
        <div class="table-search">
          <input type="search" class="search-inp" id="tbl-search" placeholder="Search currency code or name…" oninput="filterTable(this.value)">
          <span class="count-label" id="tbl-count"></span>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr>
              <th>Code</th><th>Name</th>
              <th>1 unit → EUR</th><th>1 EUR → units</th>
            </tr></thead>
            <tbody id="rates-body">
              <tr><td colspan="4" style="text-align:center;padding:36px;color:var(--muted)">
                <span class="spinner"></span> Loading…
              </td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <footer>
      <p>
        Using <a href="https://pypi.rosetraviss.uk/CurrencyConverter" target="_blank" rel="noopener">CurrencyConverter</a> PyPI package ·
        ECB data since 1999 ·
        Runs on <a href="https://developers.cloudflare.com/workers/languages/python/" target="_blank" rel="noopener">Cloudflare Python Workers</a> (Pyodide/WASM) ·
        Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
      </p>
    </footer>
  </div>

  <script>
    const NAMES = {
      USD:"US Dollar",EUR:"Euro",GBP:"British Pound",JPY:"Japanese Yen",
      AUD:"Australian Dollar",CAD:"Canadian Dollar",CHF:"Swiss Franc",
      CNY:"Chinese Yuan",SEK:"Swedish Krona",NOK:"Norwegian Krone",
      DKK:"Danish Krone",NZD:"New Zealand Dollar",MXN:"Mexican Peso",
      SGD:"Singapore Dollar",HKD:"Hong Kong Dollar",KRW:"South Korean Won",
      TRY:"Turkish Lira",INR:"Indian Rupee",BRL:"Brazilian Real",
      ZAR:"South African Rand",PLN:"Polish Złoty",HUF:"Hungarian Forint",
      CZK:"Czech Koruna",RON:"Romanian Leu",BGN:"Bulgarian Lev",
      IDR:"Indonesian Rupiah",MYR:"Malaysian Ringgit",PHP:"Philippine Peso",
      THB:"Thai Baht",ISK:"Icelandic Króna",ILS:"Israeli Shekel",
      AED:"UAE Dirham",SAR:"Saudi Riyal",HRK:"Croatian Kuna",
      RUB:"Russian Ruble",UAH:"Ukrainian Hryvnia",
    };

    let ratesData = {};

    async function init() {
      try {
        const res = await fetch('/api/info');
        const d = await res.json();
        if (d.error) throw new Error(d.error);

        // Hero stats
        document.getElementById('rate-date').textContent = d.latest_date;
        document.getElementById('cur-count').textContent = d.currencies.length;
        document.getElementById('pkg-version').textContent = 'currency_converter v' + (d.version || '?');
        document.getElementById('pkg-ver-inline').textContent = d.version || '?';

        // Live stats panel
        document.getElementById('stat-currencies').textContent = d.currencies.length;
        document.getElementById('stat-date').textContent = d.latest_date;
        document.getElementById('stat-earliest').textContent = d.earliest_date;
        document.getElementById('stat-latest').textContent = d.latest_date;

        // Bounds list
        const bl = document.getElementById('bounds-list');
        bl.innerHTML = d.bounds.slice(0,20).map(b =>
          `<div class="bounds-row"><span>${b.currency}</span>  ${b.first} → ${b.last}</div>`
        ).join('') + (d.bounds.length > 20 ? `<div style="color:var(--muted);margin-top:4px">…and ${d.bounds.length-20} more</div>` : '');

        // Populate selects
        const currencies = d.currencies.sort();
        ratesData = {};
        d.rates.forEach(r => ratesData[r.currency] = r.eur_per_unit);
        ['from-cur','to-cur','hist-from','hist-to'].forEach(id => {
          const sel = document.getElementById(id);
          sel.innerHTML = currencies.map(c => `<option value="${c}">${c}</option>`).join('');
        });
        document.getElementById('from-cur').value = 'USD';
        document.getElementById('to-cur').value = 'EUR';
        document.getElementById('hist-from').value = 'EUR';
        document.getElementById('hist-to').value = 'USD';

        // Table
        renderTable('');

      } catch(e) {
        document.getElementById('rate-date').textContent = 'Error';
        console.error(e);
      }
    }

    function renderTable(filter) {
      const rows = Object.entries(ratesData)
        .filter(([c]) => !filter ||
          c.toLowerCase().includes(filter.toLowerCase()) ||
          (NAMES[c]||'').toLowerCase().includes(filter.toLowerCase()))
        .sort(([a],[b]) => a.localeCompare(b));
      document.getElementById('tbl-count').textContent = rows.length + ' currencies';
      document.getElementById('rates-body').innerHTML = rows.map(([c, eurPerUnit]) =>
        `<tr>
          <td><span class="cc">${c}</span></td>
          <td style="color:var(--muted)">${NAMES[c]||'—'}</td>
          <td><span class="rv">${eurPerUnit.toFixed(6)}</span></td>
          <td><span class="ev">${(1/eurPerUnit).toFixed(4)}</span></td>
        </tr>`).join('');
    }
    function filterTable(v) { renderTable(v); }

    async function doConvert() {
      const btn = document.getElementById('conv-btn');
      const amount = parseFloat(document.getElementById('amount-in').value);
      const from   = document.getElementById('from-cur').value;
      const to     = document.getElementById('to-cur').value;
      const panel  = document.getElementById('result-panel');
      const resAmt = document.getElementById('res-amount');
      const resMeta= document.getElementById('res-meta');
      const resIn  = document.getElementById('result-in');
      if (isNaN(amount)||amount<0) { resAmt.innerHTML='<span class="result-error">Enter a valid amount</span>'; panel.classList.add('show'); return; }
      btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>Converting…';
      try {
        const r = await fetch(`/api/convert?amount=${amount}&from=${from}&to=${to}`);
        const d = await r.json();
        if (d.error) throw new Error(d.error);
        const fmt = n => n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4});
        resAmt.textContent = `${fmt(d.result)} ${to}`;
        resMeta.textContent = `1 ${from} = ${d.rate.toFixed(6)} ${to}  ·  data date: ${d.date}  ·  c.convert(${amount}, '${from}', '${to}')`;
        resIn.value = d.result.toFixed(4);
        panel.classList.add('show');
      } catch(e) { resAmt.innerHTML=`<span class="result-error">Error: ${e.message}</span>`; resMeta.textContent=''; panel.classList.add('show'); }
      finally { btn.disabled=false; btn.innerHTML='Convert'; }
    }

    async function doHistorical() {
      const amount = parseFloat(document.getElementById('hist-amount').value)||100;
      const from   = document.getElementById('hist-from').value;
      const to     = document.getElementById('hist-to').value;
      const d      = document.getElementById('hist-date').value;
      const el     = document.getElementById('hist-result');
      el.innerHTML = '<span class="spinner"></span>';
      try {
        const r = await fetch(`/api/convert?amount=${amount}&from=${from}&to=${to}&date=${d}`);
        const data = await r.json();
        if (data.error) throw new Error(data.error);
        el.textContent = `${amount} ${from} = ${data.result.toFixed(4)} ${to}  (${d})`;
      } catch(e) { el.innerHTML=`<span style="color:#f87171">${e.message}</span>`; }
    }

    document.getElementById('swap-btn').addEventListener('click', () => {
      const f=document.getElementById('from-cur'), t=document.getElementById('to-cur');
      [f.value, t.value] = [t.value, f.value];
    });
    document.getElementById('amount-in').addEventListener('keydown', e => { if(e.key==='Enter') doConvert(); });

    init();
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)


def parse_qs(url_str: str) -> dict:
    """Extract query parameters from a URL string."""
    query = {}
    if "?" in url_str:
        qs = url_str.split("?", 1)[1].split("#")[0]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query[k] = v
    return query


# ─────────────────────────────────────────────────────────────────────────────
# Route: GET /api/info
# Returns live data extracted directly from the CurrencyConverter instance:
#   c.currencies, c.bounds, and the rates computed via c.convert()
# ─────────────────────────────────────────────────────────────────────────────

async def handle_info():
    try:
        c = get_converter()

        currencies = sorted(c.currencies)

        # c.bounds -> {currency: (first_date, last_date)}
        bounds_data = []
        earliest = None
        latest = None
        for cur in currencies:
            try:
                first, last = c.bounds[cur]
                bounds_data.append({
                    "currency": cur,
                    "first": str(first),
                    "last":  str(last),
                })
                if earliest is None or first < earliest:
                    earliest = first
                if latest is None or last > latest:
                    latest = last
            except Exception:
                pass

        # Compute EUR rate for each currency via c.convert()
        rates = []
        for cur in currencies:
            if cur == "EUR":
                rates.append({"currency": "EUR", "eur_per_unit": 1.0})
                continue
            try:
                eur_per_unit = c.convert(1.0, cur, "EUR")
                rates.append({"currency": cur, "eur_per_unit": eur_per_unit})
            except Exception:
                pass

        # Try to get package version
        try:
            import importlib.metadata
            version = importlib.metadata.version("currency-converter")
        except Exception:
            version = "unknown"

        return json_response({
            "currencies":    currencies,
            "bounds":        bounds_data,
            "rates":         rates,
            "earliest_date": str(earliest) if earliest else "unknown",
            "latest_date":   str(latest)   if latest   else "unknown",
            "version":       version,
            "ecb_url":       ECB_URL,
            "single_day_url": SINGLE_DAY_ECB_URL,
        })

    except Exception as e:
        return json_response({"error": str(e)}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# Route: GET /api/convert?amount=100&from=USD&to=EUR[&date=YYYY-MM-DD]
# Calls c.convert() from the actual currency_converter package
# ─────────────────────────────────────────────────────────────────────────────

async def handle_convert(query: dict):
    try:
        amount   = float(query.get("amount", "100"))
        from_cur = query.get("from", "USD").upper()
        to_cur   = query.get("to",   "EUR").upper()
        date_str = query.get("date", "")

        c = get_converter()

        if from_cur not in c.currencies:
            return json_response({"error": f"{from_cur} is not a supported currency"}, status=400)
        if to_cur not in c.currencies:
            return json_response({"error": f"{to_cur} is not a supported currency"}, status=400)

        # Build kwargs — optionally pass date=
        kwargs = {}
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                kwargs["date"] = parsed_date
            except ValueError:
                return json_response({"error": f"Invalid date format: {date_str} (use YYYY-MM-DD)"}, status=400)

        # This is the real library call:
        # c.convert(amount, 'USD', 'EUR') or c.convert(amount, 'USD', 'EUR', date=date(2013, 3, 21))
        result = c.convert(amount, from_cur, to_cur, **kwargs)
        rate   = c.convert(1.0,   from_cur, to_cur, **kwargs)

        # Get the data date from c.bounds
        try:
            _, data_date = c.bounds[from_cur]
        except Exception:
            data_date = "unknown"

        return json_response({
            "amount":   amount,
            "from":     from_cur,
            "to":       to_cur,
            "result":   result,
            "rate":     rate,
            "date":     date_str if date_str else str(data_date),
            "call":     f"c.convert({amount}, '{from_cur}', '{to_cur}'" + (f", date=date({date_str.replace('-', ', ')})" if date_str else "") + ")",
        })

    except RateNotFoundError as e:
        return json_response({"error": f"RateNotFoundError: {e}"}, status=400)
    except ValueError as e:
        return json_response({"error": str(e)}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def on_fetch(request, env):
    url  = str(request.url)
    qs   = parse_qs(url)
    path = url.split("?")[0]
    # Normalise path: strip protocol+host
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/llms.txt" or path == "/llms-full.txt":
        headers = Headers.new({"Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*"}.items())
        return Response.new(LLMS_TXT, headers=headers)

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    if path == "/api/info":
        return await handle_info()
    elif path == "/api/convert":
        return await handle_convert(qs)
    else:
        headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
        return Response.new(HTML, headers=headers)
