/**
 * Interface: ProvidesCheckoutWorkflow
 * Provider: CheckoutWorkflowService
 */

export interface CheckoutResult {
  success: boolean;
  orderId?: string;
  transactionId?: string;
}

export interface ProvidesCheckoutWorkflow {
  initiateCheckout(cartId: string, userId: string): Promise<string>;
  validateCart(cartId: string): Promise<boolean>;
  processCheckout(cartId: string, paymentMethodId: string): Promise<CheckoutResult>;
  handleCheckoutFailure(checkoutSessionId: string, failureReason: string): Promise<void>;
  getCheckoutStatus(checkoutSessionId: string): Promise<string>;
}
