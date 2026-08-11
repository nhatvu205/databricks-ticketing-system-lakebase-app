"""Runs in GitHub Actions against its disposable PostgreSQL service."""

from __future__ import annotations

import os
from uuid import UUID

import pytest

from support_app.db import LakebaseDatabase
from support_app.repository import TicketNotFound, TicketRepository


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL is not configured")
def test_schema_seed_and_crud(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    database = LakebaseDatabase.from_environment()
    repository = TicketRepository(database)
    try:
        with database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP SCHEMA IF EXISTS support_app CASCADE")

        repository.initialize()
        repository.initialize()

        stats = repository.get_stats()
        assert stats == {"total": 3, "open": 1, "in_progress": 1, "resolved": 1}

        tickets = repository.list_tickets()
        assert len(tickets) == 3
        assert all(ticket["message_count"] >= 2 for ticket in tickets)

        ticket_id = repository.create_ticket("Integration persistence check", "high", "ci@example.com")
        assert isinstance(ticket_id, UUID)
        repository.add_message(ticket_id, "Created by the integration test.", "ci@example.com")
        repository.update_status(ticket_id, "in_progress")

        ticket = repository.get_ticket(ticket_id)
        assert ticket["status"] == "in_progress"
        assert ticket["priority"] == "high"
        assert len(repository.get_messages(ticket_id)) == 1

        with pytest.raises(TicketNotFound):
            repository.add_message(
                UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
                "This foreign key must fail.",
                "ci@example.com",
            )
    finally:
        database.close()
