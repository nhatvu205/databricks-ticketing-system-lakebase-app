"""Flask application factory for the Lakebase support ticketing app."""

from __future__ import annotations

import os
import secrets
from typing import Any
from uuid import UUID

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from .constants import PRIORITIES, STATUSES
from .db import DatabaseUnavailable, LakebaseDatabase
from .repository import TicketNotFound, TicketRepository
from .validation import ValidationError, validate_message, validate_status, validate_ticket


def _request_identity() -> str:
    """Return the Databricks-authenticated email with a safe local fallback."""
    identity = (
        request.headers.get("X-Forwarded-Email")
        or request.headers.get("X-Forwarded-Preferred-Username")
        or os.getenv("LOCAL_USER_EMAIL")
        or "local-user@example.invalid"
    ).strip()
    return identity[:255] or "local-user@example.invalid"


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create the Flask application and initialize Lakebase unless injected for tests."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32)),
        TESTING=False,
        INITIALIZE_DATABASE=True,
    )
    if test_config:
        app.config.update(test_config)

    repository = app.config.get("REPOSITORY")
    if repository is None:
        repository = TicketRepository(LakebaseDatabase.from_environment())
    app.extensions["ticket_repository"] = repository

    if app.config["INITIALIZE_DATABASE"]:
        repository.initialize()

    @app.get("/")
    def index():
        selected_status = request.args.get("status", "").strip() or None
        if selected_status and selected_status not in STATUSES:
            abort(400, description="Choose a valid ticket status filter.")
        return render_template(
            "index.html",
            tickets=repository.list_tickets(selected_status),
            stats=repository.get_stats(),
            statuses=STATUSES,
            priorities=PRIORITIES,
            selected_status=selected_status,
        )

    @app.get("/tickets/<uuid:ticket_id>")
    def ticket_detail(ticket_id: UUID):
        ticket = repository.get_ticket(ticket_id)
        return render_template(
            "ticket_detail.html",
            ticket=ticket,
            messages=repository.get_messages(ticket_id),
            statuses=STATUSES,
            stats=repository.get_stats(),
        )

    @app.post("/tickets")
    def create_ticket():
        try:
            payload = validate_ticket(request.form)
            ticket_id = repository.create_ticket(
                title=payload["title"],
                priority=payload["priority"],
                created_by=_request_identity(),
            )
        except ValidationError as exc:
            flash(str(exc), "error")
            return redirect(url_for("index"))
        flash("Ticket created and saved to Lakebase.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    @app.post("/tickets/<uuid:ticket_id>/messages")
    def add_message(ticket_id: UUID):
        try:
            payload = validate_message(request.form)
            repository.add_message(
                ticket_id=ticket_id,
                message_text=payload["message_text"],
                author=_request_identity(),
            )
        except ValidationError as exc:
            flash(str(exc), "error")
        else:
            flash("Message added and saved to Lakebase.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    @app.post("/tickets/<uuid:ticket_id>/status")
    def update_status(ticket_id: UUID):
        try:
            status = validate_status(request.form.get("status", ""))
            repository.update_status(ticket_id, status)
        except ValidationError as exc:
            flash(str(exc), "error")
        else:
            flash("Ticket status updated.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    @app.get("/healthz")
    def healthz():
        try:
            repository.healthcheck()
        except DatabaseUnavailable:
            return jsonify(status="unavailable"), 503
        return jsonify(status="ok"), 200

    @app.errorhandler(TicketNotFound)
    def handle_missing_ticket(_: TicketNotFound):
        return render_template("error.html", title="Ticket not found", message="This ticket does not exist or was removed."), 404

    @app.errorhandler(DatabaseUnavailable)
    def handle_database_error(_: DatabaseUnavailable):
        return render_template(
            "error.html",
            title="Temporarily unavailable",
            message="The support data store is waking up or unavailable. Please try again shortly.",
        ), 503

    @app.errorhandler(400)
    def handle_bad_request(error):
        return render_template("error.html", title="Invalid request", message=error.description), 400

    return app
