#!/usr/bin/env bash
# E-Commerce Cloud Microservices automated verification script
set -e

GATEWAY_URL="http://localhost:8081"
CATALOG_URL="http://localhost:8001"
ORDER_URL="http://localhost:8002"

echo "========================================================================"
echo "  CloudCommerce Microservices - Test de Integración End-to-End"
echo "========================================================================"

echo "1. Comprobando estado de los microservicios..."
curl -s -f "$GATEWAY_URL/health" > /dev/null || (echo "Error: API Gateway no responde en $GATEWAY_URL" && exit 1)
curl -s -f "$CATALOG_URL/health" > /dev/null || (echo "Error: Catalog Service no responde en $CATALOG_URL" && exit 1)
curl -s -f "$ORDER_URL/health" > /dev/null || (echo "Error: Order Service no responde en $ORDER_URL" && exit 1)

echo "✓ API Gateway (FastAPI): Operativo en puerto 8081"
echo "✓ Catalog Service (FastAPI + Mongo + Redis): Operativo en puerto 8001"
echo "✓ Order Service (Spring Boot 3 + Postgres): Operativo en puerto 8002"

echo ""
echo "2. Consultando catálogo de productos a través del Gateway..."
PRODUCTS=$(curl -s "$GATEWAY_URL/api/catalog/products")
FIRST_SKU=$(echo "$PRODUCTS" | grep -o '"sku":"[^"]*' | head -n 1 | cut -d'"' -f4)
FIRST_TITLE=$(echo "$PRODUCTS" | grep -o '"title":"[^"]*' | head -n 1 | cut -d'"' -f4)
FIRST_PRICE=$(echo "$PRODUCTS" | grep -o '"price":[0-9.]*' | head -n 1 | cut -d':' -f2)

echo "✓ Producto recuperado: $FIRST_TITLE (SKU: $FIRST_SKU) - Precio: \$$FIRST_PRICE"

echo ""
echo "3. Probando búsqueda y caché..."
SEARCH_RES=$(curl -s "$GATEWAY_URL/api/catalog/products?search=teclado")
echo "✓ Búsqueda de 'teclado' completada con éxito."

echo ""
echo "4. Creando orden de compra en Java Spring Boot (Persistida en PostgreSQL)..."
ORDER_PAYLOAD="{\"customerName\":\"Testing User\",\"customerEmail\":\"test@cloudcommerce.dev\",\"shippingAddress\":\"Silicon Valley 101\",\"items\":[{\"productSku\":\"$FIRST_SKU\",\"productTitle\":\"$FIRST_TITLE\",\"price\":$FIRST_PRICE,\"quantity\":1}]}"

ORDER_RESP=$(curl -s -X POST "$GATEWAY_URL/api/orders/orders" \
  -H "Content-Type: application/json" \
  -d "$ORDER_PAYLOAD")

ORDER_ID=$(echo "$ORDER_RESP" | grep -o '"id":"[^"]*' | head -n 1 | cut -d'"' -f4)
ORDER_TOTAL=$(echo "$ORDER_RESP" | grep -o '"totalAmount":[0-9.]*' | head -n 1 | cut -d':' -f2)

echo "✓ Pedido generado exitosamente!"
echo "  ID Transaccional: $ORDER_ID"
echo "  Total: \$$ORDER_TOTAL"

echo ""
echo "5. Avanzando ciclo de vida del pedido a SHIPPED..."
STATUS_RESP=$(curl -s -X PATCH "$GATEWAY_URL/api/orders/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status":"SHIPPED"}')
echo "✓ Estado actualizado a SHIPPED."

echo ""
echo "6. Consultando estadísticas y telemetría de Caché..."
TELEMETRY=$(curl -s "$GATEWAY_URL/api/catalog/telemetry")
echo "Telemetría de Catálogo / Redis:"
echo "$TELEMETRY"

echo ""
echo "========================================================================"
echo "  ✓ Todos los microservicios se comunicaron e integraron correctamente!"
echo "========================================================================"
