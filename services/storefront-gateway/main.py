from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="CloudCommerce API Gateway & Storefront", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8001")
ORDER_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8002")

# Load HTML files dynamically
STOREFRONT_FILE = os.path.join(os.path.dirname(__file__), "storefront.html")
ADMIN_FILE = os.path.join(os.path.dirname(__file__), "admin.html")

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def serve_storefront():
    try:
        with open(STOREFRONT_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception:
        if os.path.exists("storefront.html"):
            with open("storefront.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        return HTMLResponse(content="<h1>Storefront not found</h1>", status_code=404)

@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin.html", response_class=HTMLResponse)
def serve_admin():
    try:
        with open(ADMIN_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception:
        if os.path.exists("admin.html"):
            with open("admin.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        return HTMLResponse(content="<h1>Admin console not found</h1>", status_code=404)

@app.get("/health")
async def health():
    cat_ok = False
    ord_ok = False

    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            r = await client.get(f"{CATALOG_URL}/health")
            cat_ok = r.status_code == 200
        except Exception:
            pass

        try:
            r = await client.get(f"{ORDER_URL}/health")
            ord_ok = r.status_code == 200
        except Exception:
            pass

    return {
        "status": "healthy",
        "service": "api-gateway",
        "catalog_service_healthy": cat_ok,
        "order_service_healthy": ord_ok
    }

# Reverse Proxy for Catalog Microservice
@app.api_route("/api/catalog/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_catalog(request: Request, path: str):
    url = f"{CATALOG_URL}/api/v1/{path}"
    if request.url.query:
        url += f"?{request.url.query}"

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

# Reverse Proxy for Order Microservice
@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_order(request: Request, path: str):
    url = f"{ORDER_URL}/api/v1/{path}"
    if request.url.query:
        url += f"?{request.url.query}"

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
