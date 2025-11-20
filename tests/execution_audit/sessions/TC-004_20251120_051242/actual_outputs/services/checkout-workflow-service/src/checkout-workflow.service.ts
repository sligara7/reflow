import { Injectable, Logger } from '@nestjs/common';
import { CanManageInventory } from '../../common/interfaces/can-manage-inventory.interface';
import { CanProcessPayments } from '../../common/interfaces/can-process-payments.interface';
import { CanFulfillOrders } from '../../common/interfaces/can-fulfill-orders.interface';
import {
  ProvidesCheckoutWorkflow,
  CheckoutResult
} from '../../common/interfaces/provides-checkout-workflow.interface';
import { HasLogging } from '../../common/traits/has-logging.trait';
import { TracksMetrics } from '../../common/traits/tracks-metrics.trait';
import { RequiresAuth } from '../../common/traits/requires-auth.trait';

/**
 * CheckoutWorkflowService - Workflow Orchestrator
 *
 * Implements wide inheritance pattern: 4 capabilities (depth=1, width=4)
 * - ProvidesCheckoutWorkflow (domain capability)
 * - HasLogging (behavior trait)
 * - TracksMetrics (behavior trait)
 * - RequiresAuth (behavior trait)
 *
 * Dependency Injection Pattern:
 * - Constructor injection with interface types (NOT concrete classes)
 * - Depends on: CanManageInventory, CanProcessPayments, CanFulfillOrders
 *
 * Workflow Coordination:
 * - ALL checkout coordination logic stays LOCAL in this service
 * - NOT distributed across domain services
 * - Includes compensation logic (refund payment, release inventory on failure)
 */
@Injectable()
export class CheckoutWorkflowService
  implements ProvidesCheckoutWorkflow, HasLogging, TracksMetrics, RequiresAuth {

  readonly logger = new Logger(CheckoutWorkflowService.name);

  /**
   * DEPENDENCY INJECTION via Constructor
   * Using INTERFACE types, not concrete class types
   * This enables:
   * - Easy testing (mock interfaces)
   * - Multiple implementations (different facilities)
   * - Loose coupling
   */
  constructor(
    private readonly inventoryService: CanManageInventory,
    private readonly paymentService: CanProcessPayments,
    private readonly orderService: CanFulfillOrders
  ) {}

  // ===================================================================
  // ProvidesCheckoutWorkflow Implementation
  // ===================================================================

  async initiateCheckout(cartId: string, userId: string): Promise<string> {
    this.logInfo('Initiating checkout', { cartId, userId });
    this.incrementCounter('checkout.initiated');

    const checkoutSessionId = `session_${Date.now()}`;
    return checkoutSessionId;
  }

  async validateCart(cartId: string): Promise<boolean> {
    this.logInfo('Validating cart', { cartId });
    this.incrementCounter('checkout.validations');

    // Mock validation logic
    return true;
  }

  /**
   * WORKFLOW COORDINATION - Stays LOCAL in this orchestrator service
   * Coordinates 5-step workflow: validate → check stock → reserve → pay → order
   * Includes COMPENSATION LOGIC on failure
   */
  async processCheckout(cartId: string, paymentMethodId: string): Promise<CheckoutResult> {
    this.logInfo('Starting checkout process', { cartId });
    this.incrementCounter('checkout.initiated');

    try {
      // Step 1: Validate cart
      const cart = await this.getCartDetails(cartId);
      const validCart = await this.validateCart(cartId);
      if (!validCart) {
        throw new Error('Cart validation failed');
      }

      // Step 2: Check inventory availability
      const stockCheck = await this.inventoryService.checkStockAvailability({
        items: cart.items
      });

      if (!stockCheck.available) {
        throw new Error(
          `Items unavailable: ${stockCheck.unavailableItems.map(i => i.productId).join(', ')}`
        );
      }

      // Step 3: Reserve inventory
      const reservation = await this.inventoryService.reserveInventory({
        orderId: cart.id,
        items: cart.items
      });

      // Step 4: Process payment (with COMPENSATION on failure)
      let paymentResult;
      try {
        paymentResult = await this.paymentService.processPayment({
          amount: cart.total,
          paymentMethodId: paymentMethodId
        });
      } catch (error) {
        // COMPENSATION: Release inventory reservation
        this.logError('Payment failed, releasing inventory', error);
        await this.inventoryService.releaseInventoryReservation(reservation.reservationId);
        throw error;
      }

      // Step 5: Create order (with COMPENSATION on failure)
      let orderId;
      try {
        orderId = await this.orderService.createOrder({
          cartId: cart.id,
          items: cart.items,
          total: cart.total,
          paymentId: paymentResult.transactionId
        });
      } catch (error) {
        // COMPENSATION: Refund payment AND release inventory
        this.logError('Order creation failed, refunding payment and releasing inventory', error);
        await this.paymentService.refundPayment(paymentResult.transactionId);
        await this.inventoryService.releaseInventoryReservation(reservation.reservationId);
        throw error;
      }

      // Step 6: Send confirmation (best effort, don't roll back on failure)
      try {
        await this.orderService.sendOrderConfirmation(orderId);
      } catch (error) {
        this.logError('Failed to send confirmation email', error);
        // Don't roll back - order is already created and paid
      }

      this.incrementCounter('checkout.completed');
      this.logInfo('Checkout completed successfully', { orderId });

      return {
        success: true,
        orderId: orderId,
        transactionId: paymentResult.transactionId
      };

    } catch (error) {
      this.logError('Checkout failed', error);
      this.incrementCounter('checkout.failed');
      throw error;
    }
  }

  async handleCheckoutFailure(checkoutSessionId: string, failureReason: string): Promise<void> {
    this.logError('Handling checkout failure', new Error(failureReason), { checkoutSessionId });
    // Compensation logic already handled in processCheckout
  }

  async getCheckoutStatus(checkoutSessionId: string): Promise<string> {
    this.logInfo('Getting checkout status', { checkoutSessionId });
    return 'pending';
  }

  // ===================================================================
  // HasLogging Implementation
  // ===================================================================

  logInfo(message: string, context?: object): void {
    this.logger.log(message, context);
  }

  logError(message: string, error: Error, context?: object): void {
    this.logger.error(message, error.stack, context);
  }

  logDebug(message: string, context?: object): void {
    this.logger.debug(message, context);
  }

  // ===================================================================
  // TracksMetrics Implementation
  // ===================================================================

  incrementCounter(metric: string, value: number = 1): void {
    console.log(`[METRIC] Counter ${metric} += ${value}`);
  }

  recordTiming(metric: string, duration: number): void {
    console.log(`[METRIC] Timing ${metric}: ${duration}ms`);
  }

  setGauge(metric: string, value: number): void {
    console.log(`[METRIC] Gauge ${metric} = ${value}`);
  }

  // ===================================================================
  // RequiresAuth Implementation
  // ===================================================================

  async validateToken(token: string): Promise<boolean> {
    return true; // Mock implementation
  }

  async getCurrentUser(token: string): Promise<any> {
    return { id: 'user1', email: 'test@example.com', roles: ['customer'] };
  }

  checkPermission(user: any, permission: string): boolean {
    return true; // Mock implementation
  }

  // ===================================================================
  // Private Helper Methods
  // ===================================================================

  private async getCartDetails(cartId: string): Promise<any> {
    return {
      id: cartId,
      items: [
        { productId: 'prod_1', quantity: 2 },
        { productId: 'prod_2', quantity: 1 }
      ],
      total: 99.99
    };
  }
}
