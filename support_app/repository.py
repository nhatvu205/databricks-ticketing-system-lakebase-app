"""Transactional, parameterized access to support tickets in Lakebase."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import psycopg

from .db import DatabaseUnavailable, LakebaseDatabase

SQL_DIRECTORY = Path(__file__).resolve().parent.parent / "sql"


class TicketNotFound(LookupError):
    """Raised when a requested ticket does not exist."""


class TicketRepository:
    def __init__(self, database: LakebaseDatabase):
        self.database = database

    def initialize(self) -> None:
        self.database.wait_until_ready()
        schema_sql = (SQL_DIRECTORY / "001_schema.sql").read_text(encoding="utf-8")
        seed_sql = (SQL_DIRECTORY / "002_seed.sql").read_text(encoding="utf-8")
        with self.database.connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_xact_lock(91820461)")
                    cursor.execute(schema_sql)
                    cursor.execute(seed_sql)

    def healthcheck(self) -> None:
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

    def list_tickets(self, status: str | None = None) -> list[dict]:
        query = """
            SELECT
                t.ticket_id, t.title, t.status, t.priority, t.created_by,
                t.created_at, t.updated_at, COUNT(m.message_id)::integer AS message_count
            FROM support_app.tickets AS t
            LEFT JOIN support_app.ticket_messages AS m ON m.ticket_id = t.ticket_id
            WHERE (%s IS NULL OR t.status = %s)
            GROUP BY t.ticket_id
            ORDER BY
                CASE t.status WHEN 'open' THEN 1 WHEN 'in_progress' THEN 2 ELSE 3 END,
                CASE t.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
                t.created_at DESC
        """
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (status, status))
                return list(cursor.fetchall())

    def get_ticket(self, ticket_id: UUID) -> dict:
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ticket_id, title, status, priority, created_by, created_at, updated_at
                    FROM support_app.tickets
                    WHERE ticket_id = %s
                    """,
                    (ticket_id,),
                )
                ticket = cursor.fetchone()
        if ticket is None:
            raise TicketNotFound()
        return ticket

    def get_messages(self, ticket_id: UUID) -> list[dict]:
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT message_id, ticket_id, message_text, author, created_at
                    FROM support_app.ticket_messages
                    WHERE ticket_id = %s
                    ORDER BY created_at ASC
                    """,
                    (ticket_id,),
                )
                return list(cursor.fetchall())

    def create_ticket(self, title: str, priority: str, created_by: str) -> UUID:
        with self.database.connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO support_app.tickets (title, priority, created_by)
                        VALUES (%s, %s, %s)
                        RETURNING ticket_id
                        """,
                        (title, priority, created_by),
                    )
                    return cursor.fetchone()["ticket_id"]

    def add_message(self, ticket_id: UUID, message_text: str, author: str) -> UUID:
        try:
            with self.database.connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO support_app.ticket_messages (ticket_id, message_text, author)
                            VALUES (%s, %s, %s)
                            RETURNING message_id
                            """,
                            (ticket_id, message_text, author),
                        )
                        return cursor.fetchone()["message_id"]
        except DatabaseUnavailable as exc:
            if isinstance(exc.__cause__, psycopg.errors.ForeignKeyViolation):
                raise TicketNotFound() from exc
            raise

    def update_status(self, ticket_id: UUID, status: str) -> None:
        with self.database.connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE support_app.tickets
                        SET status = %s, updated_at = now()
                        WHERE ticket_id = %s
                        RETURNING ticket_id
                        """,
                        (status, ticket_id),
                    )
                    if cursor.fetchone() is None:
                        raise TicketNotFound()

    def get_stats(self) -> dict:
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*)::integer AS total,
                        COUNT(*) FILTER (WHERE status = 'open')::integer AS open,
                        COUNT(*) FILTER (WHERE status = 'in_progress')::integer AS in_progress,
                        COUNT(*) FILTER (WHERE status = 'resolved')::integer AS resolved
                    FROM support_app.tickets
                    """
                )
                return cursor.fetchone()
