import pytest

from support_app.validation import ValidationError, validate_message, validate_status, validate_ticket


def test_ticket_validation_normalizes_valid_input():
    assert validate_ticket({"title": "  VPN outage ", "priority": "HIGH"}) == {
        "title": "VPN outage",
        "priority": "high",
    }


@pytest.mark.parametrize(
    "form",
    [
        {"title": "  ", "priority": "medium"},
        {"title": "ab", "priority": "medium"},
        {"title": "x" * 121, "priority": "medium"},
        {"title": "Valid title", "priority": "immediate"},
    ],
)
def test_ticket_validation_rejects_invalid_values(form):
    with pytest.raises(ValidationError):
        validate_ticket(form)


@pytest.mark.parametrize("message", ["", "  ", "x" * 2001])
def test_message_validation_rejects_invalid_values(message):
    with pytest.raises(ValidationError):
        validate_message({"message_text": message})


def test_status_validation_whitelists_statuses():
    assert validate_status("IN_PROGRESS") == "in_progress"
    with pytest.raises(ValidationError):
        validate_status("deleted")
