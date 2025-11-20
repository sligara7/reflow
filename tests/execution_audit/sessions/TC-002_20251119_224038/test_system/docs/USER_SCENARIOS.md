# User Scenarios

## User Persona: Online Shopper

**Name**: Sarah Customer
**Role**: Online shopper
**Goals**: Purchase products quickly and track orders

## Scenario 1: Create Order

1. Sarah browses products and adds items to cart
2. Sarah initiates checkout
3. System creates order with unique order ID
4. System processes payment
5. System sends order confirmation
6. Sarah receives order confirmation email

**Expected Outcome**: Order created successfully, payment charged, confirmation sent

## Scenario 2: Check Order Status

1. Sarah wants to check order status
2. Sarah provides order ID
3. System retrieves order details
4. System includes payment status information
5. Sarah sees complete order status (order info + payment info)

**Expected Outcome**: Complete order status with payment information displayed

## Scenario 3: Cancel Order

1. Sarah decides to cancel order
2. Sarah requests order cancellation
3. System cancels order
4. System refunds payment automatically
5. System sends cancellation confirmation
6. Sarah receives confirmation of cancellation and refund

**Expected Outcome**: Order cancelled, payment refunded, confirmation sent

## Scenario 4: Concurrent Orders

1. Multiple customers create orders simultaneously
2. Each order gets a unique ID
3. No race conditions or duplicate orders
4. All orders processed successfully

**Expected Outcome**: All concurrent orders created with unique IDs
