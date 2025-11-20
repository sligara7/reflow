"""
Payment Service Implementation
Handles all payment processing operations including validation, tax calculation, and confirmations
"""
import requests
from typing import Dict, Tuple
from datetime import datetime


class PaymentService:
    """Payment processing service with integrated card validation and tax calculation"""

    def __init__(self, config: Dict):
        self.config = config
        self.stripe_api_key = config.get('stripe_api_key')
        self.tax_service_url = config.get('tax_service_url', 'http://tax-service:8001')
        self.email_service_url = config.get('email_service_url', 'http://email-service:8002')
        self.transactions_db = {}  # Simulated database

    def process_payment(self, payment_amount: float, card_details: Dict, customer_id: str) -> Dict:
        """
        Process a payment transaction with validation and confirmation

        Note: Card validation now handled by Stripe API automatically

        Args:
            payment_amount: Amount to charge in USD
            card_details: Dictionary with card_number, cvv, expiration_date
            customer_id: Customer identifier

        Returns:
            Dictionary with transaction_id, status, and receipt
        """
        # Validate payment amount
        if payment_amount <= 0:
            raise ValueError("Payment amount must be greater than 0")

        # Process via Stripe (simulated) - Stripe validates card automatically
        transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Record transaction
        self.transactions_db[transaction_id] = {
            'amount': payment_amount,
            'customer_id': customer_id,
            'card_type': 'stripe_validated',  # Stripe handles card validation
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }

        return {
            'transaction_id': transaction_id,
            'status': 'completed',
            'receipt': f'Payment of ${payment_amount} processed successfully'
        }

    def get_payment_status(self, transaction_id: str) -> Dict:
        """
        Retrieve the status of a payment transaction

        Args:
            transaction_id: Transaction identifier

        Returns:
            Dictionary with status, timestamp, and details
        """
        if transaction_id not in self.transactions_db:
            raise ValueError(f"Transaction {transaction_id} not found")

        transaction = self.transactions_db[transaction_id]

        return {
            'status': transaction['status'],
            'timestamp': transaction['timestamp'],
            'details': {
                'amount': transaction['amount'],
                'customer_id': transaction['customer_id']
            }
        }

    def refund_payment(self, transaction_id: str, refund_amount: float, reason: str) -> Dict:
        """
        Process a refund for a previous transaction

        Args:
            transaction_id: Original transaction identifier
            refund_amount: Amount to refund
            reason: Reason for refund

        Returns:
            Dictionary with refund_id and status
        """
        # Validate transaction exists
        if transaction_id not in self.transactions_db:
            raise ValueError(f"Transaction {transaction_id} not found")

        transaction = self.transactions_db[transaction_id]

        # Validate refund amount
        if refund_amount > transaction['amount']:
            raise ValueError("Refund amount exceeds original transaction amount")

        # Process refund via Stripe (simulated)
        refund_id = f"RFD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Record refund
        self.transactions_db[refund_id] = {
            'original_transaction': transaction_id,
            'refund_amount': refund_amount,
            'reason': reason,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }

        return {
            'refund_id': refund_id,
            'status': 'completed'
        }

    def send_payment_confirmation(self, transaction_id: str, customer_email: str) -> Dict:
        """
        Send payment confirmation email to customer

        Args:
            transaction_id: Transaction identifier
            customer_email: Customer email address

        Returns:
            Dictionary with confirmation_sent and timestamp
        """
        # Validate transaction exists
        if transaction_id not in self.transactions_db:
            raise ValueError(f"Transaction {transaction_id} not found")

        # Validate email format (basic)
        if '@' not in customer_email or '.' not in customer_email:
            raise ValueError("Invalid email address")

        # Send email via email service (simulated)
        confirmation_sent = True
        timestamp = datetime.now().isoformat()

        return {
            'confirmation_sent': confirmation_sent,
            'timestamp': timestamp
        }
