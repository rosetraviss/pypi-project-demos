import json
from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return Response(
            json.dumps({"error": "Python worker is running, but pycryptodomex (required by ErisPulse-BiliParser -> bilibili-api-python) is not supported by Pyodide/Cloudflare Workers due to native C extensions."}),
            headers={"content-type": "application/json"},
            status=200
        )
