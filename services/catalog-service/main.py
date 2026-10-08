from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import os
import json
import redis
from pymongo import MongoClient

app = FastAPI(title="E-Commerce Catalog Service", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Product(BaseModel):
    id: Optional[str] = None
    sku: str = Field(..., example="TECH-PRO-01")
    title: str = Field(..., example="Ultra-Fast Cloud Laptop")
    description: str = Field(..., example="Next-gen developer workstation")
    price: float = Field(..., gt=0, example=1999.99)
    category: str = Field(..., example="hardware")
    stock: int = Field(..., ge=0, example=50)
    image_url: Optional[str] = Field(default="")

class StockDecrementRequest(BaseModel):
    quantity: int = Field(default=1, gt=0)

# Environment & Connections
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/catalog")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

mongo_client = None
products_col = None
cache = None

stats = {
    "cache_hits": 0,
    "cache_misses": 0,
    "mongo_queries": 0
}

SEED_PRODUCTS = [
    {
        "sku": "DEV-M3-PRO",
        "title": "M3 Pro Developer Workstation 32GB",
        "description": "Estación de trabajo de alta gama para compilación y virtualización",
        "price": 2199.00,
        "category": "hardware",
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80"
    },
    {
        "sku": "KB-MECH-RGB",
        "title": "Teclado Mecánico Hot-Swap RGB",
        "description": "Switches táctiles lubricados, keycaps PBT y conexión Bluetooth 5.2",
        "price": 139.50,
        "category": "perifericos",
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80"
    },
    {
        "sku": "MON-4K-UW34",
        "title": "Monitor Curvo Ultra-Wide 34\" 4K",
        "description": "Panel IPS 144Hz con hub USB-C integrado y entrega de energía 90W",
        "price": 689.00,
        "category": "monitores",
        "stock": 22,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&q=80"
    },
    {
        "sku": "DESK-STAND-PRO",
        "title": "Escritorio Ergonómico Elevable Eléctrico",
        "description": "Motor dual ultrasilencioso con memoria de altura y tablero de madera sólida",
        "price": 449.00,
        "category": "muebles",
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=500&q=80"
    },
    {
        "sku": "AUDIO-ANC-700",
        "title": "Auriculares Inalámbricos Cancelación de Ruido",
        "description": "Cancelación de ruido activa adaptativa y batería de 40 horas",
        "price": 279.99,
        "category": "audio",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"
    },
    {
        "sku": "DOCK-TB4-HUB",
        "title": "Docking Station Thunderbolt 4 12-en-1",
        "description": "Conectividad total para triple pantalla 4K y ethernet Gigabit",
        "price": 189.00,
        "category": "perifericos",
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=500&q=80"
    }
]

def init_connections():
    global mongo_client, products_col, cache
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = mongo_client.get_database()
        products_col = db["products"]
        # Seed if empty
        if products_col.count_documents({}) == 0:
            products_col.insert_many([p.copy() for p in SEED_PRODUCTS])
            print("[INFO] MongoDB catalog seeded successfully with initial products.")
    except Exception as e:
        print(f"[WARN] Error connecting to MongoDB: {e}")
        products_col = None

    try:
        cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
        cache.ping()
    except Exception as e:
        print(f"[WARN] Error connecting to Redis: {e}")
        cache = None

@app.on_event("startup")
def startup_event():
    init_connections()

@app.get("/health")
def health():
    mongo_ok = False
    redis_ok = False
    if products_col is not None:
        try:
            products_col.database.command("ping")
            mongo_ok = True
        except Exception:
            pass

    if cache is not None:
        try:
            cache.ping()
            redis_ok = True
        except Exception:
            pass

    return {
        "status": "healthy",
        "service": "catalog-service",
        "framework": "FastAPI",
        "mongo_connected": mongo_ok,
        "redis_connected": redis_ok,
        "stats": stats
    }

@app.get("/api/v1/products", response_model=List[Product])
def list_products(category: Optional[str] = None, search: Optional[str] = None):
    cache_key = f"products:cat_{category}:q_{search}"

    if cache:
        try:
            cached = cache.get(cache_key)
            if cached:
                stats["cache_hits"] += 1
                return json.loads(cached)
        except Exception:
            pass

    stats["cache_misses"] += 1
    items = []

    if products_col is not None:
        try:
            query = {}
            if category:
                query["category"] = category
            if search:
                query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                    {"sku": {"$regex": search, "$options": "i"}}
                ]

            stats["mongo_queries"] += 1
            for doc in products_col.find(query):
                doc["id"] = str(doc.get("_id"))
                doc.pop("_id", None)
                items.append(doc)
        except Exception as e:
            print(f"[ERROR] Mongo read error: {e}")
            items = []

    if not items:
        # Fallback to in-memory seeds if mongo was unreachable
        for p in SEED_PRODUCTS:
            if category and p.get("category") != category:
                continue
            if search and search.lower() not in p.get("title", "").lower() and search.lower() not in p.get("description", "").lower():
                continue
            item = p.copy()
            item["id"] = item["sku"]
            items.append(item)

    if cache:
        try:
            cache.setex(cache_key, 60, json.dumps(items))
        except Exception:
            pass

    return items

@app.get("/api/v1/categories")
def list_categories():
    if cache:
        try:
            cached = cache.get("categories:all")
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    cats = set()
    if products_col is not None:
        try:
            for c in products_col.distinct("category"):
                cats.add(c)
        except Exception:
            pass

    if not cats:
        cats = {p["category"] for p in SEED_PRODUCTS}

    result = sorted(list(cats))
    if cache:
        try:
            cache.setex("categories:all", 120, json.dumps(result))
        except Exception:
            pass

    return result

@app.get("/api/v1/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    if products_col is not None:
        try:
            query = {"sku": product_id}
            if ObjectId.is_valid(product_id):
                query = {"$or": [{"_id": ObjectId(product_id)}, {"sku": product_id}]}
            doc = products_col.find_one(query)
            if doc:
                doc["id"] = str(doc.get("_id"))
                doc.pop("_id", None)
                return doc
        except Exception as e:
            print(f"[ERROR] {e}")

    for p in SEED_PRODUCTS:
        if p["sku"] == product_id:
            item = p.copy()
            item["id"] = item["sku"]
            return item

    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/v1/products", status_code=status.HTTP_201_CREATED)
def create_product(product: Product):
    doc = product.model_dump()
    if products_col is not None:
        try:
            res = products_col.insert_one(doc)
            doc["id"] = str(res.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        doc["id"] = doc["sku"]
        SEED_PRODUCTS.append(doc)

    # Invalidate all product caches
    if cache:
        try:
            keys = cache.keys("products:*")
            if keys:
                cache.delete(*keys)
            cache.delete("categories:all")
        except Exception:
            pass

    return doc

@app.post("/api/v1/products/{product_id}/stock-decrement")
def decrement_stock(product_id: str, req: StockDecrementRequest):
    if products_col is not None:
        try:
            query = {"sku": product_id}
            if ObjectId.is_valid(product_id):
                query = {"$or": [{"_id": ObjectId(product_id)}, {"sku": product_id}]}

            product = products_col.find_one(query)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            if product.get("stock", 0) < req.quantity:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {product.get('stock')}")

            products_col.update_one(query, {"$inc": {"stock": -req.quantity}})
            new_stock = product.get("stock", 0) - req.quantity

            if cache:
                keys = cache.keys("products:*")
                if keys:
                    cache.delete(*keys)

            return {
                "message": "Stock decremented successfully",
                "product_sku": product["sku"],
                "remaining_stock": new_stock
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Stock decremented (simulated)", "remaining_stock": 50}

@app.get("/api/v1/telemetry")
def get_telemetry():
    total_prods = products_col.count_documents({}) if products_col is not None else len(SEED_PRODUCTS)
    hit_rate = 0.0
    total_reqs = stats["cache_hits"] + stats["cache_misses"]
    if total_reqs > 0:
        hit_rate = round((stats["cache_hits"] / total_reqs) * 100, 1)

    return {
        "cache_hits": stats["cache_hits"],
        "cache_misses": stats["cache_misses"],
        "cache_hit_rate_pct": hit_rate,
        "mongo_queries": stats["mongo_queries"],
        "total_catalog_products": total_prods,
        "caching_strategy": "Redis Cache-Aside with Write-Invalidation"
    }
