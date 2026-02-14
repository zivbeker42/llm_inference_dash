import os
import httpx
import json
from fastapi import FastAPI, Request, Response, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge, Histogram

app = FastAPI()

# --- Prometheus Metrics ---
instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

REQUESTS_BY_TENANT = Counter(
    "requests_by_tenant",
    "Total number of requests by tenant",
    ["org_unit", "team", "app_id", "model"]
)
# More metrics will be added here

# --- Environment Variables ---
VLLM_MOCK_SERVER_URL = os.getenv("VLLM_MOCK_SERVER_URL", "http://vllm-mock-server:8000")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "super-secret-key")

# --- Authentication ---
def get_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != GATEWAY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# --- Proxy Logic ---
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    # Authenticate request
    try:
        get_api_key(request)
    except HTTPException as e:
        return Response(content=e.detail, status_code=e.status_code)

    # Extract labels for metrics
    org_unit = request.headers.get("X-Org-Unit", "unknown")
    team = request.headers.get("X-Team", "unknown")
    app_id = request.headers.get("X-App-Id", "unknown")

    model = "unknown"
    if request.method == "POST" and path == "v1/chat/completions":
        try:
            body = await request.json()
            model = body.get("model", "unknown")
        except json.JSONDecodeError:
            pass # Ignore if body is not valid JSON

    REQUESTS_BY_TENANT.labels(org_unit=org_unit, team=team, app_id=app_id, model=model).inc()

    # Proxy the request
    async with httpx.AsyncClient() as client:
        url = f"{VLLM_MOCK_SERVER_URL}/{path}"

        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("x-api-key", None) # Do not forward our own API key

        rp_req = client.build_request(
            request.method,
            url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
            timeout=60.0,
        )

        try:
            rp_resp = await client.send(rp_req)

            # Here we can also extract metrics from the response
            # For example, token counts if the mock server provides them

            return Response(
                content=rp_resp.content,
                status_code=rp_resp.status_code,
                headers=dict(rp_resp.headers),
            )
        except httpx.RequestError as e:
            return Response(content=f"Error proxying request: {e}", status_code=500)

