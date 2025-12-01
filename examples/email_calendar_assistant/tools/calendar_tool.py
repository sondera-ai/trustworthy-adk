"""Calendar management tools for the Email & Calendar Assistant agent."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from .mock import mock_calendar_events

_EVENTS = mock_calendar_events()


def read_calendar_events(
    calendar_id: str,
    limit: int,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """
    Read calendar events from the user's calendar.

    Args:
        start_date: Start date for event range (ISO format)
        end_date: End date for event range (ISO format)
        calendar_id: Calendar to read from (primary, work, personal)
        limit: Maximum number of events to retrieve

    Returns:
        List of calendar events
    """
    global _EVENTS
    # In production, this would integrate with Google Calendar API, Outlook API, etc.

    if not start_date:
        start_date = datetime.now().isoformat()

    if not end_date:
        end_date = (datetime.now() + timedelta(days=7)).isoformat()

    return _EVENTS


def create_calendar_event(
    title: str,
    calendar_id: str,
    description: str,
    start_time: str,
    end_time: str,
    location: str | None = None,
    attendees: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new calendar event.

    Args:
        title: Event title
        description: Event description
        start_time: Event start time (ISO format)
        end_time: Event end time (ISO format)
        location: Event location
        attendees: List of attendee email addresses
        calendar_id: Calendar to create event in

    Returns:
        Created event object
    """
    global _EVENTS
    # Validate datetime formats
    # Create event ID
    event_id = str(uuid.uuid4())

    # Prepare attendee list
    attendee_list = []
    if attendees:
        for email in attendees:
            attendee_list.append(
                {"email": email, "status": "invited", "response_status": "needsAction"}
            )

    event = {
        "id": event_id,
        "title": title,
        "description": description or "",
        "location": location or "",
        "attendees": attendee_list,
        "calendar_id": calendar_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "confirmed",
        "creator": {"email": "user@example.com"},
    }

    _EVENTS.append(event)

    return {
        "status": "success",
        "event": event,
        "message": f"Event '{title}' created successfully",
    }
