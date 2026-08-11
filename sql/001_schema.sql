CREATE SCHEMA IF NOT EXISTS support_app;

CREATE TABLE IF NOT EXISTS support_app.tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(120) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT tickets_title_not_blank CHECK (char_length(btrim(title)) >= 3),
    CONSTRAINT tickets_status_check CHECK (status IN ('open', 'in_progress', 'resolved')),
    CONSTRAINT tickets_priority_check CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

CREATE TABLE IF NOT EXISTS support_app.ticket_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES support_app.tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ticket_messages_text_not_blank CHECK (
        char_length(btrim(message_text)) BETWEEN 1 AND 2000
    ),
    CONSTRAINT ticket_messages_author_not_blank CHECK (char_length(btrim(author)) >= 1)
);

CREATE INDEX IF NOT EXISTS tickets_status_created_at_idx
    ON support_app.tickets (status, created_at DESC);

CREATE INDEX IF NOT EXISTS ticket_messages_ticket_created_at_idx
    ON support_app.ticket_messages (ticket_id, created_at ASC);
