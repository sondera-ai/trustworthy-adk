"""Payment processing tools for the Payment Agent."""

from typing import Any


def initiate_refund(transaction_id: str, amount: float) -> dict[str, Any]:
    """
    Initiate a refund for a transaction.

    Args:
        transaction_id: Transaction to refund
        amount: Amount to refund

    Returns:
        Status of refund operation
    """
    return {
        "status": "ok",
        "transaction_id": transaction_id,
        "refunded_amount": float(amount),
    }


def send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Send an email to a recipient.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content

    Returns:
        Status of email sending operation
    """
    return {
        "status": "ok",
        "to": to,
        "subject": subject,
        "body": body,
    }
