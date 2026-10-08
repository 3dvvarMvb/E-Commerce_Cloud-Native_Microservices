# Project Directives: E-Commerce Cloud-Native Microservices

Arquitectura políglota de comercio electrónico de alta escala. Combina Java Spring Boot 3 para servicios transaccionales con Python FastAPI para catálogos y analítica rápida.

## Responsabilidades de los Subagentes en este Proyecto
- **system-architect**: Diseñar el patrón Saga y comunicación asíncrona basada en eventos entre el servicio de catálogo, órdenes e inventario.
- **backend-engineer**:
  - `services/catalog-service/`: FastAPI + PyMongo + Redis Caché.
  - `services/order-service/`: Java 21 / Spring Boot 3.3 con JPA, Hibernate y validaciones.
- **devops-sre-engineer**: Gestionar redes independientes, healthchecks en Compose y manifiestos K8s en `k8s/`.
- **qa-security-auditor**: Verificar protección contra inyección NoSQL y pruebas de carga en endpoints de catálogo.
