# Astrocyte Integration Tavus Demo

This is a Cloudflare Python Worker demonstrating the real `astrocyte-integration-tavus` PyPI package.

## Deployment Details

- **Demo URL**: https://astrocyte-integration-tavus.pypi.rosetraviss.uk
- **Package Page**: https://pypi.rosetraviss.uk/astrocyte-integration-tavus
- **Primary Host**: https://pypi.rosetraviss.uk

## Overview

The demo provides a web interface and an API proxy for the Tavus Conversational Video API, allowing you to easily list conversations and view conversation details from your browser.

Since Cloudflare Workers using Pyodide have networking restrictions on synchronous HTTP requests, this demo interacts with the Tavus API directly via a `js_fetch` shim for full compatibility, ensuring fast, non-blocking requests while demonstrating the conceptual usage of the library.

## API Endpoints

### `GET /api/info`
Returns general metadata about the installed library version.

### `GET /api/list_conversations`
List Tavus conversations. Requires providing an API key in the `Authorization` header.

#### Query Parameters
- `limit` (integer, optional)
- `page` (integer, optional)
- `status` (string, optional)

### `GET /api/get_conversation`
Get details for a specific Tavus conversation. Requires providing an API key in the `Authorization` header.

#### Query Parameters
- `conversation_id` (string, required): The ID of the conversation to fetch.
