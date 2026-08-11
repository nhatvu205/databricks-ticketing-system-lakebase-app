INSERT INTO support_app.tickets (
    ticket_id, title, status, priority, created_by, created_at, updated_at
) VALUES
    (
        '11111111-1111-4111-8111-111111111111',
        'VPN disconnects every hour',
        'open',
        'high',
        'alex.morgan@example.com',
        '2026-01-15 08:30:00+00',
        '2026-01-15 08:30:00+00'
    ),
    (
        '22222222-2222-4222-8222-222222222222',
        'Finance dashboard data is stale',
        'in_progress',
        'urgent',
        'jamie.lee@example.com',
        '2026-01-16 09:00:00+00',
        '2026-01-16 09:00:00+00'
    ),
    (
        '33333333-3333-4333-8333-333333333333',
        'Request access for a new analyst',
        'resolved',
        'taylor.chen@example.com',
        '2026-01-17 10:15:00+00',
        '2026-01-17 10:15:00+00'
    )
ON CONFLICT (ticket_id) DO NOTHING;

INSERT INTO support_app.ticket_messages (
    message_id, ticket_id, message_text, author, created_at
) VALUES
    (
        '11111111-aaaa-4111-8111-111111111111',
        '11111111-1111-4111-8111-111111111111',
        'The VPN reconnects, but it drops again after about an hour.',
        'alex.morgan@example.com',
        '2026-01-15 08:35:00+00'
    ),
    (
        '11111111-bbbb-4111-8111-111111111111',
        '11111111-1111-4111-8111-111111111111',
        'Support is reviewing gateway logs and will share an update today.',
        'support.agent@example.com',
        '2026-01-15 09:10:00+00'
    ),
    (
        '22222222-aaaa-4222-8222-222222222222',
        '22222222-2222-4222-8222-222222222222',
        'Revenue totals still show yesterday\'s data after the morning refresh.',
        'jamie.lee@example.com',
        '2026-01-16 09:05:00+00'
    ),
    (
        '22222222-bbbb-4222-8222-222222222222',
        'The upstream ingestion job is being re-run; monitoring the next refresh.',
        'data.platform@example.com',
        '2026-01-16 09:25:00+00'
    ),
    (
        '33333333-aaaa-4333-8333-333333333333',
        'Please grant analyst access to the customer-retention dashboard.',
        'taylor.chen@example.com',
        '2026-01-17 10:20:00+00'
    ),
    (
        '33333333-bbbb-4333-8333-333333333333',
        'Access was granted and the analyst confirmed they can open the dashboard.',
        'identity.team@example.com',
        '2026-01-17 10:40:00+00'
    )
ON CONFLICT (message_id) DO NOTHING;
