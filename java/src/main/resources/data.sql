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
