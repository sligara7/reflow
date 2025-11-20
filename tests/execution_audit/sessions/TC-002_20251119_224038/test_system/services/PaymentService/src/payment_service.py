"""
PaymentService - Handles payment processing and confirmations
"""
from typing import Dict, Any
import uuid
from datetime import datetime


class PaymentService:
    """Service for processing payments"""

    def __init__(self):
        """Initialize PaymentService"""
        self.payments = {}  # In-memory payment storage (database in production)

    def process_payment(self, order_id: str, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment for an order

        Args:
            order_id: Order identifier
            payment_details: Payment information (amount, method, etc.)

        Returns:
            Dictionary with payment_id and payment_status
        """
        payment_id = str(uuid.uuid4())

        # Create payment record
        payment = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": payment_details.get("amount", 0.0),
            "status": "COMPLETED",  # Simplified - always succeeds
            "processed_at": datetime.now().isoformat()
        }

        # Store payment
        self.payments[payment_id] = payment

        return {
            "payment_id": payment_id,
            "payment_status": payment["status"]
        }

    def send_order_confirmation(self, order_id: str, customer_email: str) -> Dict[str, str]:
        """
        Send order confirmation to customer

        Args:
            order_id: Order identifier
            customer_email: Customer email address

        Returns:
            Dictionary with confirmation status
        """
        # Simplified - just log confirmation
        print(f"Sending order confirmation for {order_id} to {customer_email}")

        return {
            "confirmation_status": "SENT"
        }

    def refund_payment(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """
        Process payment refund for cancelled order

        ADDED: Fix for TEST-001 - Order cancellation doesn't refund payment

        Args:
            payment_id: Payment identifier to refund
            amount: Amount to refund

        Returns:
            Dictionary with refund_status and refund_transaction_id
        """
        if payment_id not in self.payments:
            return {
                "refund_status": "FAILED",
                "error": "Payment not found"
            }

        payment = self.payments[payment_id]

        # Update payment status to REFUNDED
        payment["status"] = "REFUNDED"
        payment["refunded_at"] = datetime.now().isoformat()
        payment["refund_amount"] = amount

        refund_transaction_id = str(uuid.uuid4())

        return {
            "refund_status": "SUCCESS",
            "refund_transaction_id": refund_transaction_id
        }

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status by payment ID

        ADDED: Fix for TEST-002 - Order status doesn't include payment info
        Enables OrderService to query payment status via new interface

        Args:
            payment_id: Payment identifier

        Returns:
            Dictionary with payment status information
        """
        if payment_id not in self.payments:
            return {
                "error": "Payment not found",
                "payment_status": "NOT_FOUND"
            }

        payment = self.payments[payment_id]
        return {
            "payment_id": payment_id,
            "payment_status": payment["status"],
            "amount": payment["amount"],
            "processed_at": payment.get("processed_at"),
            "refunded_at": payment.get("refunded_at")
        }
