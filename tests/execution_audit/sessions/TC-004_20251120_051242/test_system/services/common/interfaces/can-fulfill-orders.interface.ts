/**
 * Interface: CanFulfillOrders
 * Provider: OrderFulfillmentService
 */

export interface CreateOrderRequest {
  cartId: string;
  items: any[];
  total: number;
  paymentId: string;
}

export interface CanFulfillOrders {
  createOrder(request: CreateOrderRequest): Promise<string>;
  sendOrderConfirmation(orderId: string): Promise<boolean>;
  cancelOrder(orderId: string): Promise<string>;
}
