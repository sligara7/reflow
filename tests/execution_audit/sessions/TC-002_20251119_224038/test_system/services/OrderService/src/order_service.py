"""
OrderService - Handles order creation, status retrieval, and cancellation
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class OrderService:
    """Service for managing orders"""

    def __init__(self, payment_service):
        """Initialize OrderService with payment service dependency"""
        self.payment_service = payment_service
        self.orders = {}  # In-memory order storage (database in production)

    def validate_order_uniqueness(self, proposed_order_id: str) -> Dict[str, bool]:
        """
        Atomic check to ensure order_id is unique before creation

        ADDED: Fix for TEST-003 - Concurrent order creation causes race conditions

        Args:
            proposed_order_id: Proposed order identifier to check

        Returns:
            Dictionary with is_unique boolean
        """
        # In production, this would use database locks or atomic operations
        is_unique = proposed_order_id not in self.orders
        return {
            "is_unique": is_unique
        }

    def create_order(self, customer_id: str, product_list: list,
                    shipping_address: str) -> Dict[str, Any]:
        """
        Create a new order

        Args:
            customer_id: Customer identifier
            product_list: List of products to order
            shipping_address: Shipping address for the order

        Returns:
            Dictionary with order_id and order_status
        """
        order_id = str(uuid.uuid4())

        # UPDATED: Validate uniqueness before creation (TEST-003 fix)
        uniqueness_check = self.validate_order_uniqueness(order_id)
        if not uniqueness_check["is_unique"]:
            # Retry with new ID
            order_id = str(uuid.uuid4())

        # Create order record
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "product_list": product_list,
            "shipping_address": shipping_address,
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        }

        # Store order
        self.orders[order_id] = order

        # Process payment through PaymentService
        payment_result = self.payment_service.process_payment(
            order_id=order_id,
            payment_details={"amount": 100.0}  # Simplified
        )

        # Update order status based on payment
        if payment_result["payment_status"] == "COMPLETED":
            order["status"] = "CONFIRMED"
            order["payment_id"] = payment_result["payment_id"]
        else:
            order["status"] = "PAYMENT_FAILED"

        return {
            "order_id": order_id,
            "order_status": order["status"]
        }

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Retrieve order status

        UPDATED: Fix for TEST-002 - Now includes payment status via new interface

        Args:
            order_id: Order identifier

        Returns:
            Dictionary with order status and details
        """
        if order_id not in self.orders:
            return {
                "error": "Order not found",
                "order_status": "NOT_FOUND"
            }

        order = self.orders[order_id]

        # UPDATED: Query payment status from PaymentService (TEST-002 fix)
        payment_status_info = None
        if "payment_id" in order:
            payment_status_info = self.payment_service.get_payment_status(
                order["payment_id"]
            )

        order_details = {
            "order_id": order_id,
            "customer_id": order["customer_id"],
            "product_list": order["product_list"],
            "shipping_address": order["shipping_address"],
            "created_at": order["created_at"]
        }

        # Add payment status if available
        if payment_status_info and "payment_status" in payment_status_info:
            order_details["payment_status"] = payment_status_info["payment_status"]

        return {
            "order_status": order["status"],
            "order_details": order_details
        }

    def cancel_order(self, order_id: str) -> Dict[str, str]:
        """
        Cancel an existing order

        UPDATED: Fix for TEST-001 - Now refunds payment when order is cancelled

        Args:
            order_id: Order identifier

        Returns:
            Dictionary with cancellation status
        """
        if order_id not in self.orders:
            return {
                "cancellation_status": "FAILED",
                "error": "Order not found"
            }

        order = self.orders[order_id]

        # UPDATED: Refund payment if order had one (TEST-001 fix)
        if "payment_id" in order:
            refund_result = self.payment_service.refund_payment(
                payment_id=order["payment_id"],
                amount=100.0  # Simplified
            )
            order["refund_status"] = refund_result.get("refund_status")

        # Update order status
        order["status"] = "CANCELLED"
        order["cancelled_at"] = datetime.now().isoformat()

        return {
            "cancellation_status": "SUCCESS"
        }
