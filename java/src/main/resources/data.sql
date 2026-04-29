MERGE INTO customers (id, name, date_of_birth, email_address) KEY (id) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Alice Active', DATE '1986-08-13', 'alice.active@example.com'),
    ('22222222-2222-2222-2222-222222222222', 'Bob Builder', DATE '1992-04-21', 'bob.builder@example.com'),
    ('33333333-3333-3333-3333-333333333333', 'Carla Coach', DATE '1978-11-05', 'carla.coach@example.com'),
    ('44444444-4444-4444-4444-444444444444', 'Mila Minor', DATE '2010-09-14', 'mila.minor@example.com');

MERGE INTO plans (id, title, description, duration_in_months, price) KEY (id) VALUES
    ('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Basic 1 Month', 'Flexible monthly membership plan', 1, 129.00),
    ('aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6', 'Standard 6 Months', 'Six-month commitment with reduced monthly price', 6, 599.00),
    ('aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12', 'Premium 12 Months', 'Twelve-month plan for regular training', 12, 999.00),
    ('aaaaaa24-aaaa-aaaa-aaaa-aaaaaaaaaa24', 'Elite 24 Months', 'Twenty-four-month plan for long-term training', 24, 1699.00);

MERGE INTO memberships (
    id,
    customer_id,
    plan_id,
    plan_price,
    plan_duration,
    status,
    reason,
    start_date,
    end_date,
    pause_start_date,
    pause_end_date,
    pause_reason,
    cancelled_at,
    cancellation_reason
) KEY (id) VALUES
    (
        'b7000000-0000-0000-0000-000000000001',
        '11111111-1111-1111-1111-111111111111',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'ACTIVE',
        NULL,
        DATE '2026-01-01',
        DATE '2026-12-31',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'b7000000-0000-0000-0000-000000000002',
        '22222222-2222-2222-2222-222222222222',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'ACTIVE',
        NULL,
        DATE '2026-01-01',
        DATE '2026-12-31',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'b7000000-0000-0000-0000-000000000003',
        '33333333-3333-3333-3333-333333333333',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'ACTIVE',
        NULL,
        DATE '2026-01-01',
        DATE '2026-12-31',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'b7000000-0000-0000-0000-000000000004',
        '11111111-1111-1111-1111-111111111111',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'SUSPENDED',
        'NON_PAYMENT',
        DATE '2026-01-01',
        DATE '2026-12-31',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'b7000000-0000-0000-0000-000000000005',
        '22222222-2222-2222-2222-222222222222',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'CANCELLED',
        NULL,
        DATE '2026-01-01',
        DATE '2026-12-31',
        NULL,
        NULL,
        NULL,
        TIMESTAMP WITH TIME ZONE '2026-02-01 10:00:00+00:00',
        'Seed cancellation'
    ),
    (
        'b7000000-0000-0000-0000-000000000006',
        '33333333-3333-3333-3333-333333333333',
        'aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12',
        999,
        12,
        'PAUSED',
        NULL,
        DATE '2026-01-01',
        DATE '2027-01-14',
        DATE '2026-06-01',
        DATE '2026-06-14',
        'Seed pause',
        NULL,
        NULL
    );

MERGE INTO membership_billing_references (
    id,
    membership_id,
    external_invoice_id,
    external_invoice_reference,
    due_date,
    status,
    created_at,
    updated_at
) KEY (id) VALUES
    (
        'c7000000-0000-0000-0000-000000000001',
        'b7000000-0000-0000-0000-000000000001',
        'seed-external-open-overdue',
        'seed-local-open-overdue',
        DATE '2026-05-01',
        'OPEN',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00'
    ),
    (
        'c7000000-0000-0000-0000-000000000002',
        'b7000000-0000-0000-0000-000000000002',
        'seed-external-open-current',
        'seed-local-open-current',
        DATE '2026-07-01',
        'OPEN',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00'
    ),
    (
        'c7000000-0000-0000-0000-000000000003',
        'b7000000-0000-0000-0000-000000000003',
        'seed-external-paid',
        'seed-local-paid',
        DATE '2026-05-01',
        'PAID',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-02-01 10:00:00+00:00'
    ),
    (
        'c7000000-0000-0000-0000-000000000004',
        'b7000000-0000-0000-0000-000000000004',
        'seed-external-suspended',
        'seed-local-suspended',
        DATE '2026-05-01',
        'OPEN',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00'
    ),
    (
        'c7000000-0000-0000-0000-000000000005',
        'b7000000-0000-0000-0000-000000000005',
        'seed-external-cancelled',
        'seed-local-cancelled',
        DATE '2026-05-01',
        'OPEN',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00'
    ),
    (
        'c7000000-0000-0000-0000-000000000006',
        'b7000000-0000-0000-0000-000000000006',
        'seed-external-paused',
        'seed-local-paused',
        DATE '2026-07-01',
        'OPEN',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00',
        TIMESTAMP WITH TIME ZONE '2026-01-01 10:00:00+00:00'
    );
