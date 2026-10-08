package com.ecommerce.orders.dto;

import com.ecommerce.orders.model.OrderStatus;
import java.math.BigDecimal;
import java.util.List;

public class OrderDtos {

    public record OrderItemRequest(
            String productSku,
            String productTitle,
            BigDecimal price,
            Integer quantity
    ) {}

    public record CreateOrderRequest(
            String customerName,
            String customerEmail,
            String shippingAddress,
            List<OrderItemRequest> items
    ) {}

    public record UpdateStatusRequest(
            OrderStatus status
    ) {}
}
