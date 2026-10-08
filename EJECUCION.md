# Guía de Ejecución Rápida: E-Commerce Cloud-Native Microservices

Bienvenido a la guía oficial de ejecución del **Proyecto 2: E-Commerce Cloud-Native Microservices**. Este proyecto fue diseñado como una pieza de ingeniería de software empresarial que demuestra dominio de **arquitecturas políglotas desacopladas, persistencia híbrida (SQL + NoSQL), caché distribuido de alto rendimiento y API Gateway**.

---

## 1. Puesta en Marcha (1 Solo Comando)

Desde esta carpeta (`02-ecommerce-cloud-microservices/`) o desde la raíz del workspace, ejecuta:

```bash
docker compose up -d --build
```

Esto levantará automáticamente 6 contenedores orquestados con dependencias de salud (`service_healthy`):
1. **PostgreSQL 16**: Base de datos relacional para el servicio de órdenes (`puerto 5433`).
2. **MongoDB 7**: Base de datos de documentos para catálogo dinámico y atributos no estructurados (`puerto 27017`).
3. **Redis 7**: Motor en memoria para caché sub-milisegundo y absorción de picos (`puerto 6380`).
4. **Catalog Service (Python 3.12 / FastAPI)**: Microservicio de catálogo y búsqueda con auto-seed de productos (`puerto 8001`).
5. **Order Service (Java 21 / Spring Boot 3.3)**: Microservicio transaccional de órdenes y estados con JPA (`puerto 8002`).
6. **Storefront Gateway (FastAPI / Reverse Proxy + Web Portal)**: Enrutador centralizado y Storefront web (`puerto 8081`).

Para verificar el estado de los contenedores:
```bash
docker compose ps
```

---

## 2. Tienda Web Interactiva y Panel de Control

Abre tu navegador web y entra a:
👉 **[http://localhost:8081](http://localhost:8081)** (o `http://localhost:8081/dashboard`)

En esta interfaz visual moderna podrás:
- **Explorar el Catálogo NoSQL**: Productos tecnológicos con fotos, etiquetas de categoría, precio y stock en tiempo real cargados desde MongoDB.
- **Búsqueda Instantánea y Filtros**: Filtrar por categorías (hardware, monitores, periféricos, audio, muebles) o buscar por texto libre.
- **Carrito de Compras y Checkout Transaccional**: Agregar múltiples productos al carrito y procesar el pedido. La solicitud es enviada a **Java Spring Boot**, persistida en **PostgreSQL** y actualiza el stock en **MongoDB**.
- **Seguimiento de Órdenes en Vivo**: Tabla conectada a PostgreSQL que muestra los pedidos creados, con botones para avanzar el estado a `SHIPPED` o `DELIVERED`.
- **Métricas de Rendimiento y Caché**: Monitorea en vivo los *Cache Hits* de Redis frente a las consultas a MongoDB, visualizando el ahorro de latencia.
- **Botón "Compra Rápida"**: Simula una transacción instantánea de prueba para validar todo el flujo de extremo a extremo.

---

## 3. Endpoints de la API (Probados vía API Gateway)

Todas las llamadas externas entran a través del Gateway (`puerto 8081`), el cual enruta el tráfico hacia los microservicios internos correspondientes:

### A. Healthcheck del Gateway y Servicios Descendentes
```bash
curl -s http://localhost:8081/health | jq
```

### B. Consultar Catálogo Completo (con Caché Redis)
```bash
curl -s http://localhost:8081/api/catalog/products | jq
```

### C. Filtrar por Categoría o Búsqueda por Texto
```bash
# Filtrar solo periféricos
curl -s "http://localhost:8081/api/catalog/products?category=perifericos" | jq

# Búsqueda por palabra clave
curl -s "http://localhost:8081/api/catalog/products?search=curvo" | jq
```

### D. Crear un Pedido en Java Spring Boot (PostgreSQL)
```bash
curl -s -X POST http://localhost:8081/api/orders/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customerName": "Juan Pérez",
    "customerEmail": "juan@empresa.com",
    "shippingAddress": "Calle Tecnológica 123",
    "items": [
      {
        "productSku": "KB-MECH-RGB",
        "productTitle": "Teclado Mecánico Hot-Swap RGB",
        "price": 139.50,
        "quantity": 2
      }
    ]
  }' | jq
```

### E. Listar Pedidos Guardados en PostgreSQL
```bash
curl -s http://localhost:8081/api/orders/orders | jq
```

### F. Actualizar Estado de un Pedido (`PATCH`)
```bash
# Reemplazar con el UUID devuelto al crear el pedido
ORDER_ID="<UUID_DEL_PEDIDO>"

curl -s -X PATCH "http://localhost:8081/api/orders/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "SHIPPED"}' | jq
```

### G. Telemetría y Ratio de Caché Redis
```bash
curl -s http://localhost:8081/api/catalog/telemetry | jq
```

---

## 4. Script de Verificación Automatizada

Hemos incluido un script en Bash que valida la integración completa de los microservicios:

```bash
./scripts/test_ecommerce.sh
```

---

## 5. Argumentos Clave para Defender este Proyecto en una Entrevista

1. **¿Por qué utilizar persistencia políglota (MongoDB + PostgreSQL)?**
   > *"En e-commerce a gran escala, el catálogo de productos requiere flexibilidad esquemática: un monitor tiene resolución y tasa de refresco, mientras que una silla tiene ergonomía y peso. MongoDB (NoSQL) permite evolucionar los atributos del catálogo sin migraciones de esquema bloqueantes. En cambio, las órdenes y facturación requieren consistencia relacional estricta (ACID) y llaves foráneas para auditoría financiera, por lo que PostgreSQL es la opción ideal."*

2. **¿Cómo implementas la estrategia de caché con Redis?**
   > *"Utilizamos el patrón Cache-Aside con invalidación en escritura. Las lecturas consultan primero a Redis; si hay cache miss, se consulta a MongoDB y se puebla Redis con un TTL de 60 segundos. Cuando un producto se crea o se actualiza su stock, se eliminan las llaves relevantes de Redis para garantizar que los clientes no lean datos obsoletos."*

3. **¿Cuál es el rol de Spring Boot 3 en esta arquitectura?**
   > *"Spring Boot 3 con Java 21 gestiona el núcleo transaccional de órdenes mediante JPA (`@Transactional`). Al recibir un pedido, calcula totales, persiste las entidades `Order` y `OrderItem` atómicamente, y comunica el decremento de inventario al servicio de catálogo."*

4. **¿Por qué es fundamental un API Gateway?**
   > *"El Gateway desacopla a los clientes web o móviles de la topología interna de la red. Centraliza políticas de CORS, enruta peticiones hacia los microservicios adecuados, y permite balancear carga y agregar rate-limiting sin tocar el código de negocio de cada microservicio."*

---

## 6. Detener el Entorno

Para apagar los contenedores:
```bash
docker compose down
```

Para reiniciar desde cero eliminando los datos de las bases de datos:
```bash
docker compose down -v
```
