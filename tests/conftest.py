from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from support_app import create_app
from support_app.db import DatabaseUnavailable
from support_app.repository import TicketNotFound


class FakeRepository:
    def __init__(self):
        self.ticket_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        self.tickets = {
            self.ticket_id: {
                "ticket_id": self.ticket_id,
                "title": "Test VPN access",
                "status": "open",
                "priority": "high",
                "created_by": "seed@example.com",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "message_count": 1,
            }
        }
        self.messages = {
            self.ticket_id: [
                {
                    "message_id": UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
                    "ticket_id": self.ticket_id,
                    "message_text": "Initial report",
                    "author": "seed@example.com",
                    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                }
            ]
        }
        self.unavailable = False

    def initialize(self):
        return None

    def healthcheck(self):
        if self.unavailable:
            raise DatabaseUnavailable()

    def list_tickets(self, status=None):
        if self.unavailable:
            raise DatabaseUnavailable()
        values = list(self.tickets.values())
        return [ticket for ticket in values if status is None or ticket["status"] == status]

    def get_ticket(self, ticket_id):
        if ticket_id not in self.tickets:
            raise TicketNotFound()
        return self.tickets[ticket_id]

    def get_messages(self, ticket_id):
        self.get_ticket(ticket_id)
        return self.messages.get(ticket_id, [])

    def create_ticket(self, title, priority, created_by):
        ticket_id = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
        self.tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "title": title,
            "status": "open",
            "priority": priority,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "message_count": 0,
        }
        self.messages[ticket_id] = []
        return ticket_id

    def add_message(self, ticket_id, message_text, author):
        self.get_ticket(ticket_id)
        self.messages[ticket_id].append(
            {
                "message_id": UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
                "ticket_id": ticket_id,
                "message_text": message_text,
                "author": author,
                "created_at": datetime.now(timezone.utc),
            }
        )

    def update_status(self, ticket_id, status):
        self.get_ticket(ticket_id)["status"] = status

    def delete_ticket(self, ticket_id):
        self.get_ticket(ticket_id)
        del self.tickets[ticket_id]
        del self.messages[ticket_id]

    def get_stats(self):
        values = list(self.tickets.values())
        return {
            "total": len(values),
            "open": sum(ticket["status"] == "open" for ticket in values),
            "in_progress": sum(ticket["status"] == "in_progress" for ticket in values),
            "resolved": sum(ticket["status"] == "resolved" for ticket in values),
        }


@pytest.fixture
def repository():
    return FakeRepository()


@pytest.fixture
def app(repository):
    return create_app(
        {
            "TESTING": True,
            "REPOSITORY": repository,
            "INITIALIZE_DATABASE": False,
            "SECRET_KEY": "test-secret",
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
