"""Runs in GitHub Actions against its disposable PostgreSQL service."""

from __future__ import annotations

import os
from uuid import UUID

import pytest

from support_app import create_app
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
                cursor.execute("SELECT current_database() AS database_name")
                assert cursor.fetchone()["database_name"].endswith("_test")
                cursor.execute("DROP SCHEMA IF EXISTS support_app CASCADE")

        repository.initialize()
        repository.initialize()

        stats = repository.get_stats()
        assert stats == {"total": 3, "open": 1, "in_progress": 1, "resolved": 1}

        tickets = repository.list_tickets()
        assert len(tickets) == 3
        assert all(ticket["message_count"] >= 2 for ticket in tickets)
        assert sum(ticket["message_count"] for ticket in tickets) == 6
        open_tickets = repository.list_tickets("open")
        assert len(open_tickets) == 1
        assert open_tickets[0]["status"] == "open"

        ticket_id = repository.create_ticket("Integration persistence check", "high", "ci@example.com")
        assert isinstance(ticket_id, UUID)
        repository.add_message(ticket_id, "Created by the integration test.", "ci@example.com")
        repository.update_status(ticket_id, "in_progress")

        ticket = repository.get_ticket(ticket_id)
        assert ticket["status"] == "in_progress"
        assert ticket["priority"] == "high"
        assert len(repository.get_messages(ticket_id)) == 1
        assert any(item["ticket_id"] == ticket_id for item in repository.list_tickets("in_progress"))

        missing_ticket_id = UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
        with pytest.raises(TicketNotFound):
            repository.get_ticket(missing_ticket_id)
        with pytest.raises(TicketNotFound):
            repository.update_status(missing_ticket_id, "resolved")

        with pytest.raises(TicketNotFound):
            repository.add_message(
                UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
                "This foreign key must fail.",
                "ci@example.com",
            )

        production_app = create_app({"TESTING": True, "SECRET_KEY": "integration-secret"})
        production_repository = production_app.extensions["ticket_repository"]
        try:
            client = production_app.test_client()
            assert client.get("/healthz").get_json() == {"status": "ok"}
            assert client.get("/").status_code == 200
            assert client.get(f"/tickets/{ticket_id}").status_code == 200
        finally:
            production_repository.database.close()
    finally:
        database.close()
