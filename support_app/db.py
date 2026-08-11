"""Lakebase and local PostgreSQL connection management."""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Iterator

import psycopg
from databricks.sdk import WorkspaceClient
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, PoolTimeout


class DatabaseUnavailable(RuntimeError):
    """Raised when a database operation cannot be completed safely."""


class RotatingOAuthConnection(psycopg.Connection):
    """A connection that creates a fresh Lakebase OAuth credential on login."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        endpoint = os.getenv("LAKEBASE_ENDPOINT")
        if not endpoint:
            raise DatabaseUnavailable("LAKEBASE_ENDPOINT is required for Lakebase authentication.")
        credential = WorkspaceClient().postgres.generate_database_credential(endpoint=endpoint)
        kwargs["password"] = credential.token
        return super().connect(conninfo, **kwargs)


class LakebaseDatabase:
    """Small connection-pool wrapper supporting Lakebase and local test PostgreSQL."""

    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    @classmethod
    def from_environment(cls) -> "LakebaseDatabase":
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            pool = ConnectionPool(
                conninfo=database_url,
                min_size=0,
                max_size=5,
                timeout=10,
                max_lifetime=2700,
                kwargs={"row_factory": dict_row},
                open=True,
            )
            return cls(pool)

        required = ("PGDATABASE", "PGHOST", "PGPORT", "PGSSLMODE", "PGUSER", "LAKEBASE_ENDPOINT")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise DatabaseUnavailable("Lakebase application resource is not configured.")
        conninfo = " ".join(
            (
                f"dbname={os.environ['PGDATABASE']}",
                f"host={os.environ['PGHOST']}",
                f"port={os.environ['PGPORT']}",
                f"user={os.environ['PGUSER']}",
                f"sslmode={os.environ['PGSSLMODE']}",
                "application_name=lakebase-support-ticketing",
            )
        )
        pool = ConnectionPool(
            conninfo=conninfo,
            connection_class=RotatingOAuthConnection,
            min_size=0,
            max_size=5,
            timeout=15,
            max_lifetime=2700,
            kwargs={"row_factory": dict_row},
            open=True,
        )
        return cls(pool)

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        try:
            with self.pool.connection() as connection:
                yield connection
        except (PoolTimeout, psycopg.Error, DatabaseUnavailable) as exc:
            raise DatabaseUnavailable("Database request failed.") from exc

    def wait_until_ready(self, attempts: int = 5) -> None:
        """Handle Lakebase scale-to-zero without exposing low-level errors to users."""
        last_error: DatabaseUnavailable | None = None
        for attempt in range(attempts):
            try:
                with self.connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                return
            except DatabaseUnavailable as exc:
                last_error = exc
                if attempt < attempts - 1:
                    time.sleep(2**attempt)
        raise DatabaseUnavailable("Database did not become ready in time.") from last_error

    def close(self) -> None:
        self.pool.close()
