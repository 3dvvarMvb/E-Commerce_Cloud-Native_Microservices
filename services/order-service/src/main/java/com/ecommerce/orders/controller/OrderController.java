package com.ecommerce.orders.controller;

import com.ecommerce.orders.dto.OrderDtos.*;
import com.ecommerce.orders.model.Order;
import com.ecommerce.orders.model.OrderItem;
import com.ecommerce.orders.model.OrderStatus;
import com.ecommerce.orders.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.*;

@RestController
@CrossOrigin(origins = "*")
public class OrderController {

    private final OrderRepository orderRepository;
    private final RestTemplate restTemplate;

    @Value("${catalog.service.url:http://catalog-service:8001}")
    private String catalogServiceUrl;

    public OrderController(OrderRepository orderRepository, RestTemplate restTemplate) {
        this.orderRepository = orderRepository;
        this.restTemplate = restTemplate;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "healthy");
        resp.put("service", "order-service");
        resp.put("framework", "Spring Boot 3.3.4 (Java 21)");
        resp.put("total_orders", orderRepository.count());
        return ResponseEntity.ok(resp);
    }

    @GetMapping("/api/v1/orders")
    public ResponseEntity<List<Order>> listOrders(@RequestParam(required = false) String email) {
        if (email != null && !email.trim().isEmpty()) {
            return ResponseEntity.ok(orderRepository.findByCustomerEmailIgnoreCaseOrderByCreatedAtDesc(email.trim()));
        }
        return ResponseEntity.ok(orderRepository.findAllByOrderByCreatedAtDesc());
    }

    @GetMapping("/api/v1/orders/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable UUID id) {
        return orderRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/api/v1/orders")
    @Transactional
    public ResponseEntity<?> createOrder(@RequestBody CreateOrderRequest req) {
        if (req.items() == null || req.items().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "El pedido debe contener al menos un producto"));
        }

        BigDecimal total = BigDecimal.ZERO;
        for (var itemReq : req.items()) {
            BigDecimal lineTotal = itemReq.price().multiply(BigDecimal.valueOf(itemReq.quantity()));
            total = total.add(lineTotal);
        }

        Order order = new Order(
                req.customerName(),
                req.customerEmail(),
                req.shippingAddress(),
                total
        );

        for (var itemReq : req.items()) {
            OrderItem item = new OrderItem(
                    itemReq.productSku(),
                    itemReq.productTitle(),
                    itemReq.price(),
                    itemReq.quantity(),
                    order
            );
            order.addItem(item);

            // Notify downstream catalog service asynchronously / best effort
            try {
                String decrementUrl = catalogServiceUrl + "/api/v1/products/" + itemReq.productSku() + "/stock-decrement";
                restTemplate.postForObject(decrementUrl, Map.of("quantity", itemReq.quantity()), Map.class);
            } catch (Exception e) {
                // Log and continue (graceful degradation)
                System.err.println("[WARN] Could not notify catalog service for stock update: " + e.getMessage());
            }
        }

        Order saved = orderRepository.save(order);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PatchMapping("/api/v1/orders/{id}/status")
    @Transactional
    public ResponseEntity<?> updateStatus(@PathVariable UUID id, @RequestBody UpdateStatusRequest req) {
        return orderRepository.findById(id).map(order -> {
            order.setStatus(req.status());
            orderRepository.save(order);
            return ResponseEntity.ok(order);
        }).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/api/v1/orders/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        List<Order> all = orderRepository.findAll();
        BigDecimal totalRevenue = all.stream()
                .map(Order::getTotalAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Map<String, Object> stats = new HashMap<>();
        stats.put("total_orders", all.size());
        stats.put("total_revenue", totalRevenue);
        stats.put("confirmed_orders", all.stream().filter(o -> o.getStatus() == OrderStatus.CONFIRMED).count());
        stats.put("shipped_orders", all.stream().filter(o -> o.getStatus() == OrderStatus.SHIPPED).count());
        return ResponseEntity.ok(stats);
    }
}
