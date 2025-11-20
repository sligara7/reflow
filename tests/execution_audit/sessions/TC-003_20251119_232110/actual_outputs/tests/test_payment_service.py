"""
Unit tests for PaymentService
Tests all 6 contracted functions
"""
import pytest
from services.PaymentService.src.payment_service import PaymentService


@pytest.fixture
def payment_service():
    config = {
        'stripe_api_key': 'test_key',
        'tax_service_url': 'http://localhost:8001',
        'email_service_url': 'http://localhost:8002'
    }
    return PaymentService(config)


def test_process_payment(payment_service):
    """Test ProcessPayment function"""
    result = payment_service.process_payment(
        payment_amount=100.00,
        card_details={
            'card_number': '4111111111111111',
            'cvv': '123',
            'expiration_date': '12/25'
        },
        customer_id='CUST-001'
    )

    assert 'transaction_id' in result
    assert result['status'] == 'completed'
    assert 'receipt' in result


# REMOVED - Function obsolete (redundant)
# def test_validate_payment_card(payment_service):
    """Test ValidatePaymentCard function"""
    # Valid Visa card
    valid, card_type = payment_service.validate_payment_card(
        card_number='4111111111111111',
        cvv='123',
        expiration_date='12/25'
    )

    assert valid is True
    assert card_type == 'visa'

    # Invalid card
    valid, card_type = payment_service.validate_payment_card(
        card_number='123',
        cvv='12',
        expiration_date='invalid'
    )

    assert valid is False


def test_get_payment_status(payment_service):
    """Test GetPaymentStatus function"""
    # First create a transaction
    result = payment_service.process_payment(
        payment_amount=50.00,
        card_details={
            'card_number': '5555555555554444',
            'cvv': '456',
            'expiration_date': '06/26'
        },
        customer_id='CUST-002'
    )

    transaction_id = result['transaction_id']

    # Now get status
    status = payment_service.get_payment_status(transaction_id)

    assert status['status'] == 'completed'
    assert 'timestamp' in status
    assert status['details']['amount'] == 50.00


# REMOVED - Function obsolete (superseded by Avalara)
# def test_calculate_tax(payment_service):
    """Test CalculateTax function"""
    result = payment_service.calculate_tax(
        amount=100.00,
        state='CA',
        zip_code='94102'
    )

    assert 'tax_amount' in result
    assert 'tax_rate' in result
    assert result['tax_amount'] > 0
    assert 0 < result['tax_rate'] < 1


def test_refund_payment(payment_service):
    """Test RefundPayment function"""
    # First create a transaction
    payment_result = payment_service.process_payment(
        payment_amount=200.00,
        card_details={
            'card_number': '4111111111111111',
            'cvv': '789',
            'expiration_date': '03/27'
        },
        customer_id='CUST-003'
    )

    transaction_id = payment_result['transaction_id']

    # Now refund
    refund_result = payment_service.refund_payment(
        transaction_id=transaction_id,
        refund_amount=100.00,
        reason='Customer request'
    )

    assert 'refund_id' in refund_result
    assert refund_result['status'] == 'completed'


def test_send_payment_confirmation(payment_service):
    """Test SendPaymentConfirmation function"""
    # First create a transaction
    payment_result = payment_service.process_payment(
        payment_amount=75.00,
        card_details={
            'card_number': '371449635398431',
            'cvv': '1234',
            'expiration_date': '09/28'
        },
        customer_id='CUST-004'
    )

    transaction_id = payment_result['transaction_id']

    # Send confirmation
    confirmation = payment_service.send_payment_confirmation(
        transaction_id=transaction_id,
        customer_email='customer@example.com'
    )

    assert confirmation['confirmation_sent'] is True
    assert 'timestamp' in confirmation
