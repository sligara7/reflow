# TC-004: TypeScript Workflow-Based Architecture Patterns

**Test Case ID**: TC-004
**Test Name**: typescript_workflow_patterns
**Language**: TypeScript
**Complexity**: Medium
**Expected Duration**: 90-120 minutes
**Version**: 1.0.0
**Created**: 2025-11-19

---

## Purpose

Validate that Reflow's v3.18.0 architectural patterns (interfaces, dependency injection, service organization strategies, wide inheritance) work correctly in **TypeScript**, demonstrating that these principles are **language-agnostic**.

---

## Test Objectives

### Primary Objectives (P0 - Must Pass)

1. ✅ **SE-02-A00 executes** - Service organization analysis runs successfully
2. ✅ **Recommends WORKFLOW-BASED** - Analysis correctly identifies high coordination complexity and recommends workflow-based organization
3. ✅ **Agent B explains recommendation** - Agent B understands WHY workflow-based is better (coordination, workflow span, operation types)
4. ✅ **Services organized by workflow** - CheckoutWorkflowService (orchestrator) + 3 supporting services (NOT domain-based like UserService, ProductService, OrderService)
5. ✅ **D1.4.5 generates TypeScript interfaces** - Interfaces generated in TypeScript (not Python Protocols or ABCs)
6. ✅ **Capability-based naming** - Interfaces use CanX, ProvidesY, HandlesZ naming (not implementation names)
7. ✅ **Dependency injection pattern** - Services use constructor injection with interface type hints
8. ✅ **Wide inheritance applied** - Services implement 3-4 capabilities (depth=1, width=3-4)
9. ✅ **Workflow coordination local** - Checkout coordination logic stays in CheckoutWorkflowService (not distributed)
10. ✅ **As-built matches architecture** - Final similarity >= 0.95

### Secondary Objectives (P1 - Should Pass)

11. ✅ **TypeScript idioms** - Async/await, Promises, proper typing
12. ✅ **NestJS patterns** - @Injectable decorators, module organization
13. ✅ **Error handling** - try/catch with typed errors
14. ✅ **Code compiles** - `tsc` or `npm run build` succeeds
15. ✅ **Tests follow conventions** - Jest test files with proper structure

---

## System Requirements

**System Name**: E-commerce Checkout System
**Domain**: E-commerce
**Primary Workflow**: Customer checkout (cart → payment → order)

**Key Characteristics** (should trigger WORKFLOW-BASED recommendation):
- **High coordination complexity** - Checkout spans 4 services with orchestration logic
- **Cross-domain workflows** - Checkout touches inventory, payment, order, notification domains
- **Workflow-heavy operations** - State management, error handling, compensation logic (not simple CRUD)
- **Distributed state risk** - If organized by domain, checkout state scattered across services

---

## Phase-by-Phase Test Scenario

### Phase 1: Basic Setup (S-00A to S-03)
**Duration**: 5 minutes

**Actions**:
1. Initialize working_memory.json
2. Set system name: "E-commerce Checkout System"
3. Set framework: UAF
4. **Set primary language: TypeScript** (critical!)

**Deliverables**:
- `context/working_memory.json` with language set to TypeScript

**Validation**:
- ✅ Language configuration: `"primary_language": "typescript"`

---

### Phase 2: Functional Analysis (FA-01 to FA-07)
**Duration**: 10 minutes

**User Requirement**:
```
As a customer, I want to complete a purchase so that I can receive my products.

Checkout Flow:
1. Validate shopping cart contents
2. Check inventory availability for all items
3. Reserve inventory for this order
4. Process payment via Stripe
5. Create order record
6. Send order confirmation email
7. On failure: Release inventory reservations, refund payment
```

**Expected Functions** (14 functions across workflow):

**Checkout Orchestration** (5 functions):
- F-001: InitiateCheckout - Start checkout process
- F-002: ValidateCart - Validate cart contents and pricing
- F-003: ProcessCheckout - Orchestrate full checkout workflow
- F-004: HandleCheckoutFailure - Handle failures with compensation
- F-005: GetCheckoutStatus - Query checkout progress

**Inventory Management** (3 functions):
- F-006: CheckStockAvailability - Check if items are in stock
- F-007: ReserveInventory - Reserve items for this order
- F-008: ReleaseInventoryReservation - Release reserved items (on failure)

**Payment Processing** (3 functions):
- F-009: ProcessPayment - Charge payment via Stripe
- F-010: RefundPayment - Refund payment (on failure)
- F-011: ValidatePaymentMethod - Validate card/payment method

**Order Management** (3 functions):
- F-012: CreateOrder - Create order record in database
- F-013: SendOrderConfirmation - Send email confirmation
- F-014: CancelOrder - Cancel order (on failure)

**Deliverables**:
- `specs/machine/functional/functional_architecture_v1.0.0.json` (14 functions)
- `specs/human/FUNCTIONAL_ARCHITECTURE.md`

**Validation**:
- ✅ 14 functions defined
- ✅ Functional flows: "Standard Checkout Flow", "Checkout Failure Flow"
- ✅ Functions span multiple domains (inventory, payment, order)

---

### Phase 3: Service Organization Analysis (SE-02-A00) ⭐ **CRITICAL TEST**
**Duration**: 10 minutes

**Tool Execution**:
```bash
python3 tools/analyze_service_organization.py /path/to/system
```

**Expected Analysis Output**:
```json
{
  "system_characteristics": {
    "coordination_complexity": "HIGH",
    "coordination_evidence": [
      "Checkout process spans 4 distinct service boundaries",
      "Requires distributed transaction management (reserve → charge → create → notify)",
      "5-step orchestration with compensation logic on failure",
      "Checkout state must be coordinated across inventory, payment, order services"
    ],
    "workflow_span": "CROSS_DOMAIN",
    "workflow_evidence": [
      "Checkout workflow touches 4 domains: cart validation, inventory, payment, order",
      "Primary workflow (ProcessCheckout) coordinates across all domains",
      "Failure handling requires compensation across multiple domains"
    ],
    "operation_types": "WORKFLOW_HEAVY",
    "operation_evidence": [
      "Orchestration logic: 5-step workflow with compensation",
      "State management: checkout progress tracking",
      "Error handling: distributed rollback/compensation",
      "NOT simple CRUD: complex business logic with cross-service coordination"
    ]
  },
  "recommendation": "WORKFLOW_BASED",
  "rationale": "High coordination complexity + cross-domain workflows + workflow-heavy operations → Organizing by workflow keeps coordination logic LOCAL within CheckoutWorkflowService instead of distributed across domain services. This reduces distributed state, simplifies error handling, and improves maintainability.",
  "anti_pattern_warning": "Domain-based organization (UserService, ProductService, OrderService) would scatter checkout logic across services, creating distributed state management problems and complex cross-service error handling."
}
```

**User Prompt** (Agent B should present):
```
Based on the analysis, which service organization strategy would you like to use?

System Characteristics:
- Coordination complexity: HIGH (checkout spans 4 services, 5-step orchestration)
- Workflow span: CROSS_DOMAIN (inventory, payment, order, notification)
- Operation types: WORKFLOW_HEAVY (orchestration, state management, compensation)

Recommendation: WORKFLOW-BASED organization

Why?
Organizing services by USER WORKFLOWS (CheckoutWorkflowService) instead of
BUSINESS DOMAINS (ProductService, OrderService) keeps coordination logic LOCAL.

Options:
1. Domain-Based - Services by business domain (ProductService, OrderService, UserService)
   ❌ NOT RECOMMENDED: Checkout logic distributed across services

2. Workflow-Based - Services by user workflows (CheckoutWorkflowService, InventoryAvailabilityService)
   ✅ RECOMMENDED: Checkout coordination stays local, simpler error handling

3. Hybrid - Workflow services for coordination + Domain services for shared capabilities

Your choice: [2]
```

**Validation**:
- ✅ Tool executes successfully
- ✅ Analysis identifies HIGH coordination complexity
- ✅ Analysis identifies CROSS_DOMAIN workflow span
- ✅ Analysis identifies WORKFLOW_HEAVY operations
- ✅ Recommendation: WORKFLOW_BASED
- ✅ Agent B explains WHY (coordination local vs distributed)
- ✅ User chooses workflow-based (option 2)
- ✅ Choice recorded in `specs/machine/service_organization_strategy.json`

**Deliverables**:
- `specs/machine/service_organization_analysis.json`
- `specs/machine/service_organization_strategy.json`

---

### Phase 4: Top-Down Design (SE-01 to SE-03)
**Duration**: 15 minutes

**Service Allocation** (following WORKFLOW-BASED strategy):

**Service 1: CheckoutWorkflowService** (Orchestrator)
- **Type**: Workflow service
- **Responsibility**: Orchestrate entire checkout process
- **Functions**: F-001 (InitiateCheckout), F-002 (ValidateCart), F-003 (ProcessCheckout), F-004 (HandleCheckoutFailure), F-005 (GetCheckoutStatus)
- **Dependencies**: Depends on InventoryAvailabilityService, PaymentProcessingService, OrderFulfillmentService
- **Language**: TypeScript
- **Framework**: NestJS

**Service 2: InventoryAvailabilityService** (Supporting)
- **Type**: Domain capability service
- **Responsibility**: Manage inventory availability and reservations
- **Functions**: F-006 (CheckStockAvailability), F-007 (ReserveInventory), F-008 (ReleaseInventoryReservation)
- **Dependencies**: None (leaf service)
- **Language**: TypeScript
- **Framework**: NestJS

**Service 3: PaymentProcessingService** (Supporting)
- **Type**: Domain capability service
- **Responsibility**: Process payments via Stripe API
- **Functions**: F-009 (ProcessPayment), F-010 (RefundPayment), F-011 (ValidatePaymentMethod)
- **Dependencies**: External (Stripe API)
- **Language**: TypeScript
- **Framework**: NestJS

**Service 4: OrderFulfillmentService** (Supporting)
- **Type**: Domain capability service
- **Responsibility**: Create orders and send notifications
- **Functions**: F-012 (CreateOrder), F-013 (SendOrderConfirmation), F-014 (CancelOrder)
- **Dependencies**: External (Email service)
- **Language**: TypeScript
- **Framework**: NestJS

**Interfaces** (4 interfaces):
1. **CanManageInventory** - Inventory operations (CheckoutWorkflowService → InventoryAvailabilityService)
2. **CanProcessPayments** - Payment operations (CheckoutWorkflowService → PaymentProcessingService)
3. **CanFulfillOrders** - Order operations (CheckoutWorkflowService → OrderFulfillmentService)
4. **ProvidesCheckoutWorkflow** - Checkout API (External → CheckoutWorkflowService)

**Validation**:
- ✅ 4 services created (1 workflow orchestrator + 3 supporting services)
- ✅ CheckoutWorkflowService contains ALL checkout coordination logic
- ✅ Supporting services provide domain capabilities (NOT orchestration)
- ✅ Service allocation follows workflow-based strategy (NOT domain-based like ProductService, OrderService)

**Deliverables**:
- `specs/machine/service_arch/CheckoutWorkflowService/service_architecture_v1.0.0.json`
- `specs/machine/service_arch/InventoryAvailabilityService/service_architecture_v1.0.0.json`
- `specs/machine/service_arch/PaymentProcessingService/service_architecture_v1.0.0.json`
- `specs/machine/service_arch/OrderFulfillmentService/service_architecture_v1.0.0.json`
- `specs/machine/interface_registry_v1.0.0.json` (4 interfaces)

---

### Phase 5: Artifacts Visualization (AV-01 to AV-04)
**Duration**: 10 minutes

**Expected ICDs** (4 interface contracts):

**ICD 1: can_manage_inventory_icd.json**
```json
{
  "interface_id": "can_manage_inventory",
  "interface_name": "CanManageInventory",
  "provider": "InventoryAvailabilityService",
  "consumers": ["CheckoutWorkflowService"],
  "protocol": "HTTP/REST",
  "operations": [
    {
      "operation_name": "checkStockAvailability",
      "http_method": "POST",
      "endpoint": "/inventory/check-availability",
      "request_schema": { "items": "array of {productId, quantity}" },
      "response_schema": { "available": "boolean", "unavailableItems": "array" }
    },
    {
      "operation_name": "reserveInventory",
      "http_method": "POST",
      "endpoint": "/inventory/reserve",
      "request_schema": { "orderId": "string", "items": "array" },
      "response_schema": { "reservationId": "string", "expiresAt": "timestamp" }
    },
    {
      "operation_name": "releaseInventoryReservation",
      "http_method": "DELETE",
      "endpoint": "/inventory/reservations/{reservationId}",
      "response_schema": { "released": "boolean" }
    }
  ]
}
```

**ICD 2: can_process_payments_icd.json** (similar structure)

**ICD 3: can_fulfill_orders_icd.json** (similar structure)

**ICD 4: provides_checkout_workflow_icd.json** (similar structure)

**Deliverables**:
- `specs/machine/interfaces/can_manage_inventory_icd.json`
- `specs/machine/interfaces/can_process_payments_icd.json`
- `specs/machine/interfaces/can_fulfill_orders_icd.json`
- `specs/machine/interfaces/provides_checkout_workflow_icd.json`

**Validation**:
- ✅ 4 ICDs generated
- ✅ Interface names use capability-based naming (CanX, ProvidesY)
- ✅ ICDs specify HTTP/REST protocol
- ✅ Request/response schemas defined

---

### Phase 6: Development Setup (D-01) ⭐ **CRITICAL TEST**
**Duration**: 15 minutes

**D-01 Actions**:

1. **Language Configuration** (already set in Phase 1)
   - Primary language: TypeScript
   - Framework: NestJS
   - Package manager: npm

2. **D1.4.5: Interface Contract Strategy** ⭐ **KEY VALIDATION**

**User Prompt** (Agent B should present):
```
Which interface contract strategy would you like to use?

1. Protocol-based with Dependency Injection (RECOMMENDED)
   - Modern, flexible, no metaclass conflicts
   - ⚠️ Note: Python-only feature (Protocols are Python 3.8+)
   - ❌ NOT AVAILABLE for TypeScript

2. Abstract Base Classes (ABC)
   - Traditional inheritance-based contracts
   - ✅ AVAILABLE for TypeScript (as TypeScript interfaces)

3. Skip interface generation
   - Manual implementation

For TypeScript projects, Option 2 generates TypeScript interfaces.

Your choice: [2]
```

**Expected Tool Execution**:
```bash
python3 tools/generate_interface_abc.py /path/to/system
```

**Expected Output** (TypeScript interfaces):

**File**: `services/common/interfaces/can-manage-inventory.interface.ts`
```typescript
/**
 * Interface: CanManageInventory
 * Provider: InventoryAvailabilityService
 * Generated from ICD: can_manage_inventory_icd.json
 */

export interface StockCheckRequest {
  items: Array<{ productId: string; quantity: number }>;
}

export interface StockCheckResponse {
  available: boolean;
  unavailableItems: Array<{ productId: string; reason: string }>;
}

export interface ReserveInventoryRequest {
  orderId: string;
  items: Array<{ productId: string; quantity: number }>;
}

export interface ReserveInventoryResponse {
  reservationId: string;
  expiresAt: Date;
}

export interface CanManageInventory {
  checkStockAvailability(request: StockCheckRequest): Promise<StockCheckResponse>;
  reserveInventory(request: ReserveInventoryRequest): Promise<ReserveInventoryResponse>;
  releaseInventoryReservation(reservationId: string): Promise<boolean>;
}
```

**File**: `services/common/interfaces/can-process-payments.interface.ts` (similar)

**File**: `services/common/interfaces/can-fulfill-orders.interface.ts` (similar)

**File**: `services/common/interfaces/provides-checkout-workflow.interface.ts` (similar)

**Behavior Mixins/Traits** (TypeScript intersection types):

**File**: `services/common/traits/has-logging.trait.ts`
```typescript
export interface HasLogging {
  readonly logger: Logger;
  logInfo(message: string, context?: object): void;
  logError(message: string, error: Error, context?: object): void;
  logDebug(message: string, context?: object): void;
}
```

**File**: `services/common/traits/tracks-metrics.trait.ts`
```typescript
export interface TracksMetrics {
  incrementCounter(metric: string, value?: number): void;
  recordTiming(metric: string, duration: number): void;
  setGauge(metric: string, value: number): void;
}
```

**File**: `services/common/traits/requires-auth.trait.ts`
```typescript
export interface RequiresAuth {
  validateToken(token: string): Promise<boolean>;
  getCurrentUser(token: string): Promise<User>;
  checkPermission(user: User, permission: string): boolean;
}
```

**Deliverables**:
- `services/common/interfaces/can-manage-inventory.interface.ts`
- `services/common/interfaces/can-process-payments.interface.ts`
- `services/common/interfaces/can-fulfill-orders.interface.ts`
- `services/common/interfaces/provides-checkout-workflow.interface.ts`
- `services/common/traits/has-logging.trait.ts`
- `services/common/traits/tracks-metrics.trait.ts`
- `services/common/traits/requires-auth.trait.ts`

**Validation**:
- ✅ Tool generates TypeScript interfaces (NOT Python Protocols or ABCs)
- ✅ Interfaces use capability-based naming (CanManageInventory, not InventoryService)
- ✅ Type definitions for request/response objects
- ✅ Async methods return `Promise<T>`
- ✅ Trait interfaces generated for wide inheritance pattern

3. **NestJS Project Setup**

**Expected Actions**:
- Initialize npm project: `npm init -y`
- Install NestJS: `npm install @nestjs/common @nestjs/core @nestjs/platform-express`
- Install TypeScript: `npm install -D typescript @types/node`
- Create `tsconfig.json` with strict typing
- Create NestJS module structure

---

### Phase 7: Implementation (D-02 to D-05) ⭐ **CRITICAL TEST**
**Duration**: 30-40 minutes

**D-02: Domain Model Implementation**

**Service 1: InventoryAvailabilityService** (example implementation)

**File**: `services/inventory-availability-service/src/inventory-availability.service.ts`
```typescript
import { Injectable, Logger } from '@nestjs/common';
import { CanManageInventory, StockCheckRequest, StockCheckResponse } from '../../common/interfaces';
import { HasLogging, TracksMetrics } from '../../common/traits';

@Injectable()
export class InventoryAvailabilityService
  implements CanManageInventory, HasLogging, TracksMetrics {

  readonly logger = new Logger(InventoryAvailabilityService.name);

  // Wide inheritance: implements 3 interfaces (depth=1, width=3)

  async checkStockAvailability(request: StockCheckRequest): Promise<StockCheckResponse> {
    this.logInfo('Checking stock availability', { items: request.items });
    this.incrementCounter('inventory.stock_checks');

    // Business logic
    const unavailableItems = [];
    for (const item of request.items) {
      const stock = await this.getStock(item.productId);
      if (stock < item.quantity) {
        unavailableItems.push({
          productId: item.productId,
          reason: `Insufficient stock: ${stock} available, ${item.quantity} requested`
        });
      }
    }

    return {
      available: unavailableItems.length === 0,
      unavailableItems
    };
  }

  async reserveInventory(request: ReserveInventoryRequest): Promise<ReserveInventoryResponse> {
    this.logInfo('Reserving inventory', { orderId: request.orderId });
    this.incrementCounter('inventory.reservations_created');

    const reservationId = this.generateReservationId();
    const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    // Store reservation in database
    await this.storeReservation(reservationId, request.orderId, request.items, expiresAt);

    return { reservationId, expiresAt };
  }

  async releaseInventoryReservation(reservationId: string): Promise<boolean> {
    this.logInfo('Releasing inventory reservation', { reservationId });
    this.incrementCounter('inventory.reservations_released');

    return await this.deleteReservation(reservationId);
  }

  // HasLogging implementation
  logInfo(message: string, context?: object): void {
    this.logger.log(message, context);
  }

  logError(message: string, error: Error, context?: object): void {
    this.logger.error(message, error.stack, context);
  }

  logDebug(message: string, context?: object): void {
    this.logger.debug(message, context);
  }

  // TracksMetrics implementation
  incrementCounter(metric: string, value: number = 1): void {
    // Metrics implementation (e.g., Prometheus)
  }

  recordTiming(metric: string, duration: number): void {
    // Metrics implementation
  }

  setGauge(metric: string, value: number): void {
    // Metrics implementation
  }

  // Private helper methods
  private async getStock(productId: string): Promise<number> {
    // Database query
    return 100;
  }

  private generateReservationId(): string {
    return `res_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async storeReservation(...args: any[]): Promise<void> {
    // Database insert
  }

  private async deleteReservation(reservationId: string): Promise<boolean> {
    // Database delete
    return true;
  }
}
```

**Service 2: CheckoutWorkflowService** (Orchestrator with DI)

**File**: `services/checkout-workflow-service/src/checkout-workflow.service.ts`
```typescript
import { Injectable, Logger } from '@nestjs/common';
import {
  CanManageInventory,
  CanProcessPayments,
  CanFulfillOrders,
  ProvidesCheckoutWorkflow
} from '../../common/interfaces';
import { HasLogging, TracksMetrics } from '../../common/traits';

@Injectable()
export class CheckoutWorkflowService
  implements ProvidesCheckoutWorkflow, HasLogging, TracksMetrics {

  readonly logger = new Logger(CheckoutWorkflowService.name);

  // Dependency Injection: Constructor injection with interface types
  constructor(
    private readonly inventoryService: CanManageInventory,
    private readonly paymentService: CanProcessPayments,
    private readonly orderService: CanFulfillOrders
  ) {}

  async processCheckout(cartId: string, paymentMethodId: string): Promise<CheckoutResult> {
    this.logInfo('Starting checkout process', { cartId });
    this.incrementCounter('checkout.initiated');

    try {
      // Step 1: Validate cart
      const cart = await this.validateCart(cartId);

      // Step 2: Check inventory availability
      const stockCheck = await this.inventoryService.checkStockAvailability({
        items: cart.items
      });

      if (!stockCheck.available) {
        throw new Error(`Items unavailable: ${stockCheck.unavailableItems.map(i => i.productId).join(', ')}`);
      }

      // Step 3: Reserve inventory
      const reservation = await this.inventoryService.reserveInventory({
        orderId: cart.id,
        items: cart.items
      });

      // Step 4: Process payment
      let paymentResult;
      try {
        paymentResult = await this.paymentService.processPayment({
          amount: cart.total,
          paymentMethodId: paymentMethodId
        });
      } catch (error) {
        // Compensation: Release inventory reservation
        await this.inventoryService.releaseInventoryReservation(reservation.reservationId);
        throw error;
      }

      // Step 5: Create order
      let order;
      try {
        order = await this.orderService.createOrder({
          cartId: cart.id,
          items: cart.items,
          total: cart.total,
          paymentId: paymentResult.transactionId
        });
      } catch (error) {
        // Compensation: Refund payment and release inventory
        await this.paymentService.refundPayment(paymentResult.transactionId);
        await this.inventoryService.releaseInventoryReservation(reservation.reservationId);
        throw error;
      }

      // Step 6: Send confirmation
      await this.orderService.sendOrderConfirmation(order.id);

      this.incrementCounter('checkout.completed');
      this.logInfo('Checkout completed successfully', { orderId: order.id });

      return {
        success: true,
        orderId: order.id,
        transactionId: paymentResult.transactionId
      };

    } catch (error) {
      this.logError('Checkout failed', error);
      this.incrementCounter('checkout.failed');
      throw error;
    }
  }

  // Workflow coordination stays LOCAL in this service
  // NOT distributed across ProductService, OrderService, UserService

  async validateCart(cartId: string): Promise<Cart> {
    // Cart validation logic
    return { id: cartId, items: [], total: 0 };
  }

  // HasLogging and TracksMetrics implementations...
}
```

**Validation**:
- ✅ Services implement interfaces (InventoryAvailabilityService implements CanManageInventory)
- ✅ Dependency injection via constructor (CheckoutWorkflowService constructor)
- ✅ Interface types used in constructor (not concrete classes)
- ✅ Wide inheritance pattern (3-4 interfaces per service: CanX + HasLogging + TracksMetrics + RequiresAuth)
- ✅ Workflow coordination stays LOCAL in CheckoutWorkflowService
- ✅ Compensation logic in orchestrator (refund payment, release inventory on failure)
- ✅ TypeScript idioms: async/await, Promises, proper typing
- ✅ NestJS patterns: @Injectable decorator

**D-03 to D-05**: Integration surfaces, service implementation, tests

**Expected Test Structure** (Jest):

**File**: `services/inventory-availability-service/src/inventory-availability.service.spec.ts`
```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { InventoryAvailabilityService } from './inventory-availability.service';

describe('InventoryAvailabilityService', () => {
  let service: InventoryAvailabilityService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [InventoryAvailabilityService],
    }).compile();

    service = module.get<InventoryAvailabilityService>(InventoryAvailabilityService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('checkStockAvailability', () => {
    it('should return available=true when all items in stock', async () => {
      const request = {
        items: [
          { productId: 'prod_1', quantity: 5 },
          { productId: 'prod_2', quantity: 3 }
        ]
      };

      const result = await service.checkStockAvailability(request);

      expect(result.available).toBe(true);
      expect(result.unavailableItems).toHaveLength(0);
    });
  });

  // More tests...
});
```

**Deliverables**:
- `services/inventory-availability-service/src/inventory-availability.service.ts`
- `services/payment-processing-service/src/payment-processing.service.ts`
- `services/order-fulfillment-service/src/order-fulfillment.service.ts`
- `services/checkout-workflow-service/src/checkout-workflow.service.ts`
- Test files for all services (.spec.ts)
- `package.json` with dependencies
- `tsconfig.json` with TypeScript configuration

---

### Phase 8: As-Built Comparison (D-06)
**Duration**: 5 minutes

**Actions**:
1. Run `generate_as_built_architecture.py` to analyze TypeScript code
2. Compare designed architecture vs as-built implementation
3. Calculate similarity score

**Expected Result**:
- Similarity >= 0.95 (should be 1.00 if no deviations)
- All 14 functions implemented
- All 4 interfaces implemented
- Services match architecture specification

**Validation**:
- ✅ Similarity score >= 0.95
- ✅ No drift detected (or minimal drift < 5%)

---

### Phase 9: Final Validation (D-Post-A02)
**Duration**: 5 minutes

**Quality Gate Checks**:
1. ✅ Architecture synchronized (similarity >= 0.95)
2. ✅ All interfaces implemented correctly
3. ✅ Service contracts match implementation
4. ✅ TypeScript compilation succeeds (`tsc` or `npm run build`)
5. ✅ Tests exist for all services
6. ✅ Workflow-based organization validated (CheckoutWorkflowService is orchestrator)
7. ✅ DI pattern validated (constructor injection)
8. ✅ Wide inheritance validated (3-4 capabilities per service)

**Deliverables**:
- `context/final_verification_report.json`

---

## Success Criteria

### Must Pass (P0)

- [x] SE-02-A00 executes and analyzes system characteristics
- [x] Analysis identifies HIGH coordination, CROSS_DOMAIN workflows, WORKFLOW_HEAVY operations
- [x] Recommendation: WORKFLOW-BASED organization
- [x] Services organized by workflow (CheckoutWorkflowService + 3 supporting services)
- [x] D1.4.5 generates TypeScript interfaces (NOT Python Protocols)
- [x] Interfaces use capability-based naming (CanManageInventory, CanProcessPayments)
- [x] Services use dependency injection (constructor injection with interface types)
- [x] Wide inheritance pattern applied (3-4 capabilities per service)
- [x] Workflow coordination stays local in CheckoutWorkflowService
- [x] Final similarity >= 0.95

### Should Pass (P1)

- [x] TypeScript idioms (async/await, Promises, proper typing)
- [x] NestJS patterns (@Injectable, module organization)
- [x] Error handling (try/catch with compensation logic)
- [x] Code compiles (`tsc` succeeds)
- [x] Tests follow Jest conventions

---

## Expected Friction Points

### Potential Friction (Low-Medium)

1. **F1**: `generate_interface_abc.py` TypeScript support
   - **Expected**: Tool should handle TypeScript interface generation
   - **Risk**: May need manual validation of generated interfaces
   - **Mitigation**: Check output matches expected TypeScript syntax

2. **F2**: NestJS DI module generation
   - **Expected**: No auto-generation of NestJS modules (manual setup)
   - **Risk**: Agent B may not know NestJS DI patterns
   - **Mitigation**: Workflow should guide Agent B with examples

3. **F3**: TypeScript compilation configuration
   - **Expected**: Manual tsconfig.json setup
   - **Risk**: Incorrect TypeScript configuration
   - **Mitigation**: Provide tsconfig.json template in workflow

---

## Test Files to Generate

### Agent B Execution (Blind)
- `AGENT_B_EXECUTION_REPORT.md` - Comprehensive execution log

### Agent A Validation (With Ground Truth)
- `AGENT_A_META_ANALYSIS.md` - Validation against expected outputs

### Artifacts to Validate
- `specs/machine/service_organization_analysis.json` - SE-02-A00 output
- `specs/machine/service_organization_strategy.json` - User choice recorded
- `specs/machine/functional/functional_architecture_v1.0.0.json` - 14 functions
- `specs/machine/service_arch/*/service_architecture_v1.0.0.json` - 4 services
- `specs/machine/interface_registry_v1.0.0.json` - 4 interfaces
- `services/common/interfaces/*.interface.ts` - TypeScript interfaces
- `services/common/traits/*.trait.ts` - Trait definitions
- `services/*/src/*.service.ts` - Service implementations with DI
- `services/*/src/*.spec.ts` - Jest tests
- `package.json` - npm dependencies
- `tsconfig.json` - TypeScript configuration

---

## Notes for Agent B

**Key Reminders**:
1. This is a **TypeScript** project, not Python - use TypeScript idioms
2. SE-02-A00 should recommend **WORKFLOW-BASED** organization (not domain-based)
3. CheckoutWorkflowService is the **orchestrator** - it contains ALL checkout coordination
4. Use **constructor injection** for dependencies (NestJS pattern)
5. Implement **3-4 capabilities per service** (wide inheritance pattern)
6. Interface names should be **capability-based** (CanX, ProvidesY, HandlesZ)
7. Use **async/await** for all service methods (TypeScript idiom)
8. Implement **compensation logic** in CheckoutWorkflowService (release inventory, refund payment on failure)

**This test validates that Reflow's architectural principles are LANGUAGE-AGNOSTIC** 🚀

---

**Version**: 1.0.0
**Created**: 2025-11-19
**Test Duration**: 90-120 minutes
**Complexity**: Medium
