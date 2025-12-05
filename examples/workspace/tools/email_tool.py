"""Email management tools for the Email & Calendar Assistant agent."""

import re
from datetime import datetime
from typing import Any

from .mock import mock_emails


def read_email(
    folder: str,
    limit: int,
) -> list[dict[str, Any]]:
    """
    Read emails from the user's mailbox.

    Args:
        folder: Email folder to read from (inbox, sent, drafts, trash)
        limit: Maximum number of emails to retrieve

    Returns:
        List of email objects with metadata and content
    """
    return mock_emails(folder, limit)


def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
) -> dict[str, Any]:
    """
    Send an email on behalf of the user.

    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Email body content (HTML or plain text)
        cc: List of CC recipients
        bcc: List of BCC recipients
        attachments: List of attachment file paths
        reply_to_id: ID of email being replied to

    Returns:
        Sent email object with status
    """
    # Validate email addresses
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    for email in to + (cc or []) + (bcc or []):
        if not email_pattern.match(email):
            return {"status": "error", "message": f"Invalid email address: {email}"}

    # In production, this would send via SMTP or email API
    sent_email = {
        "id": f"sent_{datetime.now().timestamp()}",
        "to": to,
        "cc": cc or [],
        "bcc": bcc or [],
        "subject": subject,
        "body": body,
        "attachments": attachments or [],
        "sent_time": datetime.now().isoformat(),
        "status": "sent",
    }

    return sent_email


def search_emails(
    query: str,
) -> list[dict[str, Any]]:
    """
    Search emails based on various criteria.

    Args:
        query: Search query for subject/body content

    Returns:
        List of emails matching search criteria
    """
    # In production, this would use email service search API
    # This is a mock implementation

    emails = mock_emails()
    results = []
    for email in emails:
        if query in email["subject"] or query in email["body"]:
            results.append(email)
    return results


def delete_email(email_ids: list[str], permanent: bool) -> dict[str, Any]:
    """
    Delete one or more emails.

    Args:
        email_ids: List of email IDs to delete
        permanent: If True, permanently delete; if False, move to trash

    Returns:
        Status of deletion operation
    """
    if not email_ids:
        return {"status": "error", "message": "No email IDs provided"}

    # In production, this would call email service delete API
    action = "permanently deleted" if permanent else "moved to trash"

    return {
        "status": "success",
        "message": f"{len(email_ids)} email(s) {action}",
        "deleted_ids": email_ids,
        "permanent": permanent,
        "timestamp": datetime.now().isoformat(),
    }
