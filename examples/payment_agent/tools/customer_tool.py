"""Customer management tools for the Payment Agent."""

from typing import Any


def get_customer_profile(customer_id: str) -> dict[str, Any]:
    """
    Return a customer profile with region, email, and credit card information.

    Args:
        customer_id: Customer identifier

    Returns:
        Customer profile information including region, email, and credit card details

    Demo IDs:
      - 10a2b3_us → region US
      - 10a2b3_eu → region EU
    """
    region = "EU" if customer_id == "10a2b3_eu" else "US"
    profile = {
        "customer_id": customer_id,
        "region": region,
        "email": "jsmith@gmail.com",
        "cc_number": "4321 1111 1111 1111",
    }
    return profile
