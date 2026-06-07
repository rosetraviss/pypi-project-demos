import json
import traceback
from js import Headers, Response

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="#4f46e5"/><path d="M50 15 L60 40 L85 45 L65 60 L70 85 L50 70 L30 85 L35 60 L15 45 L40 40 Z" fill="#fff"/></svg>"""

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
    }.items())
    return Response.new(json.dumps(data), headers=headers, status=status)

def parse_qs(url_str: str) -> dict:
    query = {}
    if "?" in url_str:
        qs = url_str.split("?", 1)[1].split("#")[0]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query[k] = v
    return query

async def handle_info():
    try:
        import astronomy_types
        all_attrs = dir(astronomy_types)
        funcs = [f for f in all_attrs if callable(getattr(astronomy_types, f)) and not f.startswith("_")]

        return json_response({
            "package": "astronomy-types",
            "functions": funcs,
        })
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def handle_convert(qs: dict):
    try:
        import astronomy_types
        conv_type = qs.get("type")

        if conv_type == "deg_to_hrs":
            deg = float(qs.get("deg", 0))
            res = astronomy_types.degrees_to_hours(deg)
            return json_response({
                "result": float(res),
                "call": f"degrees_to_hours({deg})"
            })

        elif conv_type == "dms_to_deg":
            d = int(qs.get("d", 0))
            m = int(qs.get("m", 0))
            s = float(qs.get("s", 0))
            # dms_to_degrees takes a DMS object
            dms = astronomy_types.DMS(d, m, s)
            res = astronomy_types.dms_to_degrees(dms)
            return json_response({
                "result": float(res),
                "call": f"dms_to_degrees(DMS({d}, {m}, {s}))"
            })

        elif conv_type == "hms_to_deg":
            h = int(qs.get("h", 0))
            m = int(qs.get("m", 0))
            s = float(qs.get("s", 0))
            # hms_to_degrees takes an HMS object
            hms = astronomy_types.HMS(h, m, s)
            res = astronomy_types.hms_to_degrees(hms)
            return json_response({
                "result": float(res),
                "call": f"hms_to_degrees(HMS({h}, {m}, {s}))"
            })

        else:
            return json_response({"error": "Unknown conversion type"}, status=400)

    except Exception as e:
        return json_response({"error": str(e), "trace": traceback.format_exc()}, status=500)

async def on_fetch(request, env):
    url = str(request.url)
    qs = parse_qs(url)
    path = url.split("?")[0]
    if "://" in path:
        path = "/" + path.split("/", 3)[-1]

    if path == "/favicon.ico":
        headers = Headers.new({"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=86400"}.items())
        return Response.new(FAVICON_SVG, headers=headers)

    elif path == "/api/info":
        return await handle_info()

    elif path == "/api/convert":
        return await handle_convert(qs)

    elif path == "/style.css":
        try:
            with open("src/style.css", "r", encoding="utf-8") as f:
                content = f.read()
            headers = Headers.new({"Content-Type": "text/css; charset=utf-8"}.items())
            return Response.new(content, headers=headers)
        except Exception as e:
            return Response.new(str(e), status=500)

    elif path == "/":
        try:
            with open("src/index.html", "r", encoding="utf-8") as f:
                content = f.read()
            headers = Headers.new({"Content-Type": "text/html; charset=utf-8"}.items())
            return Response.new(content, headers=headers)
        except Exception as e:
            return Response.new(str(e), status=500)

    # Also handle llms.txt endpoints later if requested via URL
    elif path in ["/llms.txt", "/llms-full.txt"]:
        try:
            filename = "llms.txt" if path == "/llms.txt" else "llms-full.txt"
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            headers = Headers.new({"Content-Type": "text/plain; charset=utf-8"}.items())
            return Response.new(content, headers=headers)
        except Exception:
            return Response.new("Not Found", status=404)

    return Response.new("Not Found", status=404)
