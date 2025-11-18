# Test System: Microservices Basic

**Purpose**: Simple microservices system for testing Reflow functional analysis and architecture workflows.

**Domain**: E-commerce order processing

## Functional Requirements

### FR-1: User Authentication
- Users can register with email/password
- Users can login and receive JWT token
- Users can logout (invalidate token)

### FR-2: Product Catalog
- Users can browse products by category
- Users can search products by name/description
- Users can view product details (price, stock, description)

### FR-3: Shopping Cart
- Users can add products to cart
- Users can update quantities in cart
- Users can remove products from cart
- Users can view cart total

### FR-4: Order Processing
- Users can place orders from cart
- System validates product availability
- System calculates order total with tax
- System sends order confirmation email

### FR-5: Payment Processing
- System accepts credit card payments
- System validates payment information
- System processes payment via external gateway
- System handles payment failures

### FR-6: Order Fulfillment
- Warehouse staff can view pending orders
- Warehouse staff can mark orders as shipped
- System sends shipment notification email

## Non-Functional Requirements

### NFR-1: Performance
- Product search response time < 200ms
- Order placement response time < 1s
- System can handle 1000 concurrent users

### NFR-2: Security
- All API endpoints require authentication (except login/register)
- Payment information encrypted in transit and at rest
- PCI DSS compliance for payment handling

### NFR-3: Reliability
- System availability 99.9%
- No data loss for completed orders
- Graceful degradation if payment gateway unavailable

## Expected Architecture (Ground Truth)

### Services:
1. **User Service**: Authentication, user management
2. **Product Service**: Product catalog, search, inventory
3. **Cart Service**: Shopping cart operations
4. **Order Service**: Order creation, order history
5. **Payment Service**: Payment processing integration
6. **Notification Service**: Email notifications
7. **API Gateway**: Request routing, authentication

### Key Interfaces:
- User Service → Order Service: User validation
- Product Service → Cart Service: Product details, stock check
- Cart Service → Order Service: Cart contents
- Order Service → Payment Service: Payment processing
- Order Service → Notification Service: Order confirmations
- Order Service → Product Service: Stock updates
- Payment Service → Notification Service: Payment confirmations

### Expected Functions:
1. RegisterUser
2. LoginUser
3. LogoutUser
4. BrowseProducts
5. SearchProducts
6. ViewProductDetails
7. AddToCart
8. UpdateCartQuantity
9. RemoveFromCart
10. ViewCart
11. PlaceOrder
12. ValidateProductAvailability
13. CalculateOrderTotal
14. ProcessPayment
15. ValidatePaymentInfo
16. SendOrderConfirmation
17. ViewPendingOrders
18. MarkOrderShipped
19. SendShipmentNotification

### Expected Functional Dependencies:
- PlaceOrder → ValidateProductAvailability
- PlaceOrder → CalculateOrderTotal
- PlaceOrder → ProcessPayment
- ProcessPayment → ValidatePaymentInfo
- PlaceOrder → SendOrderConfirmation
- MarkOrderShipped → SendShipmentNotification
- AddToCart → ViewProductDetails
- ViewCart → ViewProductDetails
- RegisterUser (no dependencies - entry point)
- LoginUser (no dependencies - entry point)
- BrowseProducts (no dependencies - entry point)

## Testing Notes

This test case is intentionally simple to provide:
1. Clear functional requirements
2. Predictable service allocation
3. Well-defined functional dependencies
4. Expected interface contracts

Expected workflow path: 00a-basic_setup → 01d-functional_analysis
