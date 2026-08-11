from uuid import UUID


def test_index_lists_ticket_and_stats(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test VPN access" in response.data
    assert b"Total tickets" in response.data


def test_index_rejects_unknown_status_filter(client):
    response = client.get("/?status=anything")
    assert response.status_code == 400
    assert b"valid ticket status" in response.data


def test_create_ticket_uses_authenticated_header(client, repository):
    response = client.post(
        "/tickets",
        data={"title": "Submission persistence check", "priority": "high"},
        headers={"X-Forwarded-Email": "student@example.com"},
    )
    assert response.status_code == 302
    ticket = repository.get_ticket(UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"))
    assert ticket["created_by"] == "student@example.com"
    assert ticket["priority"] == "high"


def test_create_ticket_shows_validation_error(client):
    response = client.post("/tickets", data={"title": "", "priority": "high"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ticket title must be between" in response.data


def test_ticket_detail_message_and_status_update(client, repository):
    ticket_id = repository.ticket_id
    message_response = client.post(
        f"/tickets/{ticket_id}/messages",
        data={"message_text": "Investigating now."},
        headers={"X-Forwarded-Email": "agent@example.com"},
    )
    assert message_response.status_code == 302
    assert repository.messages[ticket_id][-1]["author"] == "agent@example.com"

    status_response = client.post(f"/tickets/{ticket_id}/status", data={"status": "resolved"})
    assert status_response.status_code == 302
    assert repository.get_ticket(ticket_id)["status"] == "resolved"


def test_unknown_ticket_returns_404(client):
    response = client.get("/tickets/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
    assert response.status_code == 404


def test_healthz_reflects_database_availability(client, repository):
    assert client.get("/healthz").get_json() == {"status": "ok"}
    repository.unavailable = True
    response = client.get("/healthz")
    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable"}
