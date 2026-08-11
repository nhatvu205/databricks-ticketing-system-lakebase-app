"""Input validation for browser-submitted forms."""

from __future__ import annotations

from collections.abc import Mapping

from .constants import PRIORITIES, STATUSES


class ValidationError(ValueError):
    """A user-safe validation failure."""


def _clean(value: str | None) -> str:
    return (value or "").strip()


def validate_ticket(form: Mapping[str, str]) -> dict[str, str]:
    title = _clean(form.get("title"))
    priority = _clean(form.get("priority")).lower()
    if not 3 <= len(title) <= 120:
        raise ValidationError("Ticket title must be between 3 and 120 characters.")
    if priority not in PRIORITIES:
        raise ValidationError("Choose a valid ticket priority.")
    return {"title": title, "priority": priority}


def validate_message(form: Mapping[str, str]) -> dict[str, str]:
    message_text = _clean(form.get("message_text"))
    if not 1 <= len(message_text) <= 2000:
        raise ValidationError("Message must contain between 1 and 2,000 characters.")
    return {"message_text": message_text}


def validate_status(value: str | None) -> str:
    status = _clean(value).lower()
    if status not in STATUSES:
        raise ValidationError("Choose a valid ticket status.")
    return status
