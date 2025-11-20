/**
 * Interface: CanProcessPayments
 * Provider: PaymentProcessingService
 * Generated from ICD: can_process_payments_icd.json
 */

export interface ProcessPaymentRequest {
  amount: number;
  paymentMethodId: string;
}

export interface ProcessPaymentResponse {
  transactionId: string;
  paymentStatus: 'success' | 'failed' | 'pending';
}

export interface CanProcessPayments {
  processPayment(request: ProcessPaymentRequest): Promise<ProcessPaymentResponse>;
  refundPayment(transactionId: string): Promise<string>;
  validatePaymentMethod(paymentMethodId: string): Promise<boolean>;
}
