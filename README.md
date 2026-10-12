# E-Commerce Cloud-Native Microservices

Plataforma distribuida de comercio electrónico a gran escala que combina Java 21 (Spring Boot 3) y Python (FastAPI) con persistencia políglota (MongoDB y PostgreSQL) y caché en Redis.

## Arquitectura
- **Catálogo & Búsqueda**: Python FastAPI con MongoDB y Redis Caché
- **Órdenes & Transacciones**: Java 21 / Spring Boot 3 con PostgreSQL
- **Gateway**: Enrutamiento centralizado y balanceo
- **DevOps**: Docker Compose + Manifiestos de Kubernetes en `k8s/`

## Ejecución Rápida
```bash
# 1. Iniciar servicios con Docker Compose
docker compose up -d --build

# 2. Consultar catálogo de productos (FastAPI + Redis)
curl http://localhost:8001/api/v1/products

# 3. Crear nuevo producto
curl -X POST http://localhost:8001/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "DEV-MECH-01",
    "title": "Custom Mechanical Keyboard",
    "description": "Custom keycaps and lubed switches",
    "price": 189.99,
    "category": "hardware",
    "stock": 15
  }'
```
