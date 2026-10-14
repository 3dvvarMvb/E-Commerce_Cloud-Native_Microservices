# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Desarrolladores de software, creadores técnicos, arquitectos de sistemas y profesionales de ingeniería que buscan equipamiento y hardware de alto rendimiento, valorando la velocidad extrema de respuesta, la precisión estética y una experiencia de compra fluida y sin fricción.

## Product Purpose

AURA TECH es un Storefront moderno de comercio electrónico tecnológico que fusiona la experiencia de compra de alta gama de marcas como Apple y Shopify con una arquitectura de microservicios cloud-native real (FastAPI + MongoDB + Redis Cache-Aside, Java 21 Spring Boot 3 + PostgreSQL transaccional). El éxito del producto se mide por la inmediatez en la interacción, la precisión en los cálculos y la transparencia visual del ciclo de vida de los pedidos.

## Positioning

A diferencia de las tiendas online genéricas y plantillas de comercio electrónico convencionales, AURA TECH ofrece una experiencia táctil de hardware de precisión con telemetría en tiempo real y trazabilidad visual completa del patrón Saga de microservicios, combinando una estética minimalista titánica con rendimiento sub-milisegundo.

## Operating Context

- **Entorno:** Aplicación web de escritorio y móvil responsive (375px hasta pantallas ultrawide).
- **Interacción:** Navegación optimizada por teclado (`⌘K` / `Ctrl+K` para búsqueda, tecla `Escape` para cerrar drawers), carrito lateral deslizable (slide-over drawer) sin recarga de página y retroalimentación sonora/táctil sutil.
- **Conectividad:** API Gateway inverso desacoplado con soporte híbrido de telemetría y fallback resiliente para demostraciones locales.

## Capabilities and Constraints

- **Catálogo & Inventario Dinámico:** Microservicio FastAPI con base de datos MongoDB y Redis Cache-Aside. Badges de stock reactivos en tiempo real (`En Stock`, `¡Últimas X unidades!`, `Agotado · Preventa`) con decremento automático al comprar.
- **Bolsa / Carrito Lateral Deslizable:** Slide-over drawer estilo Shopify de 460px de ancho con cálculo reactivo de subtotal, impuestos (10%), costo de envío condicional y barra dinámica de envío gratis (umbral $200).
- **Motor de Cupones:** Validación y aplicación reactiva de códigos de descuento (`APPLE20`, `CLOUD10`, `FREESHIP`).
- **Órdenes Transaccionales & Saga:** Microservicio Spring Boot 3 con JPA/Hibernate en PostgreSQL para persistencia transaccional ACID.
- **Timeline Visual de Estado de Pedidos:** Visualizador interactivo de 5 etapas (`Confirmado`, `Inventario Asignado`, `Preparación en Hub`, `En Tránsito Courier`, `Entregado`) con progreso animado y trazabilidad de eventos.
- **Restricción Estricta:** Cero emojis como controles estructurales en la interfaz; iconografía 100% vectorial SVG.

## Brand Commitments

- **Nombre:** AURA TECH (con el descriptor Cloud-Native Architecture).
- **Voz y Tono:** Profesional, técnico, sobrio, preciso y enfocado en la excelencia de ingeniería.
- **Paleta Visual:** Modo oscuro titánico (`#07080c`, `#0e1017`, `#11131a`) con desenfoque de fondo glassmorphic (`backdrop-blur-xl`), bordes finos ultra-delgados (`border-white/[0.08]`) y acentos de color Apple Blue (`#0071E3`), Emerald Green (`#10B981`) y Amber (`#F59E0B`).
- **Tipografía:** Pila de fuentes Apple San Francisco con `Inter` para texto corrido y números tabulares monoespaciados (`JetBrains Mono`) para precios, SKUs y telemetría.

## Evidence on Hand

- `services/storefront-gateway/storefront.html`: Implementación completa del Storefront moderno, carrito slide-over drawer, badges de stock dinámicos y timeline de estado de pedidos.
- `services/storefront-gateway/main.py`: API Gateway en FastAPI con proxy reverso a catálogo y órdenes.
- `services/catalog-service/`: Microservicio de catálogo con MongoDB y Redis.
- `services/order-service/`: Microservicio de pedidos en Java 21 Spring Boot 3 con PostgreSQL.
- `docker-compose.yml` & `k8s/deployment.yaml`: Orquestación y redes independientes para todo el ecosistema.

## Product Principles

1. **Claridad y jerarquía sobre decoración innecesaria:** Cada elemento visual cumple una función transaccional o informativa clara. Números tabulares legibles para métricas y precios.
2. **Retroalimentación inmediata y física:** Toda interacción del usuario (añadir a la bolsa, aplicar cupón, cambiar cantidades) genera respuesta inmediata mediante microinteracciones, micro-sonido táctil y actualización reactiva.
3. **Visibilidad arquitectónica sin fricción de usuario:** La potencia del patrón Saga y los microservicios se expone con orgullo a través de telemetría refinada y timelines comprensibles, sin entorpecer el flujo de compra.
4. **Resiliencia ante contingencias:** La interfaz mantiene una experiencia de usuario impecable tanto con el clúster de microservicios en ejecución como en modo de demostración local interactivo.

## Accessibility & Inclusion

- Contraste de texto conforme a WCAG 2.1 AA ($\ge 4.5:1$).
- Navegación accesible por teclado y foco visible en todos los elementos interactivos.
- Ocultación semántica de iconos decorativos (`aria-hidden="true"`) y textos alternativos descriptivos.
- Compatibilidad con preferencias de movimiento reducido (`prefers-reduced-motion`).
