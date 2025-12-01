"""Transaction management tools for the Payment Agent."""

from typing import Any


def get_transactions(customer_id: str, amount: float) -> list[dict[str, Any]]:
    """
    Return transaction history for a customer filtered by amount.

    Args:
        customer_id: Customer identifier
        amount: Transaction amount to filter

    Returns:
        List of transactions matching the criteria
    """
    amt = float(amount)
    txns = [
        {"transaction_id": "001", "merchant_name": "MerchantX", "amount": amt},
        {"transaction_id": "002", "merchant_name": "MerchantX", "amount": amt},
    ]
    return txns
