# Python Interview Questions & Coding Challenges - Session 8

## Concept Questions

- How does routing work in Flask?
- What is restful service
- What are the categories of HTTP status codes (1xx, 2xx, 3xx, 4xx, 5xx)? Provide examples for each.
- What is HTTP and how does it work
- Explain the concept of idempotency in HTTP methods
- Explain the difference between HTTP and HTTPS
- Design a RESTful API for a blogging platform
- What is the MVC architecture
- What are Flask's request objects

---

## Coding Challenge:
Create a complete RESTful API for the Customer & Orders model.

```
GET    /api/customers           # Get all customers
GET    /api/customers/<id>      # Get single customer
POST   /api/customers           # Create new customer
PUT    /api/customers/<id>      # Update customer
DELETE /api/customers/<id>      # Delete customer
```

**Customer fields:**
- `id` (Integer, primary key)
- `name` (String, required)
- `email` (String, required, unique)
- `created_at` (DateTime)

```
GET    /api/orders              # Get all orders
GET    /api/orders/<id>         # Get single order
POST   /api/orders              # Create order
PUT    /api/orders/<id>         # Update order
DELETE /api/orders/<id>         # Delete order
```

**Order fields:**
- `id` (Integer, primary key)
- `customer_id` (Integer, foreign key to customers)
- `order_date` (DateTime)
- `total_amount` (Numeric)
- `status` (String, default='pending')

## Requirements
1. Validate required fields
2. Return proper HTTP status codes (200, 201, 404, 400, 500)

---
