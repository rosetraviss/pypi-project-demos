# ass-imbk Demo API

This is a Cloudflare Python Worker demo for the `ass-imbk` package, which is an Advanced SubStation Alpha (ASS) subtitle file parser.

## Usage

Visit the web interface to upload an `.ass` subtitle file. The file is uploaded to the worker, parsed with `ass-imbk`, and the script metadata, styles, and a summary of dialogue events will be displayed on the page.

### Endpoints
* `GET /` - Web interface
* `POST /api/parse` - Accepts `.ass` file content and returns metadata
