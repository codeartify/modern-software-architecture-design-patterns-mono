# modern-software-architecture-design-patterns-mono

Monorepo for a workshop that keeps the same application shape in two stacks:

- `java/`: Java 21, Spring Boot, Maven
- `python/`: Python 3.14, FastAPI, `uv` with `pyproject.toml`

## Structure

```text
.
├── java
│   ├── pom.xml
│   └── src
├── requests
│   ├── health.http
│   └── store-demo.http
└── python
    ├── pyproject.toml
    ├── src
    └── tests
```

## Workshop Exercise Structure
The `E00` to `E06` prefixes are intentional. In production many types would have simpler names, but in this workshop repo the prefixes keep IDE search results clear when multiple architecture styles implement the same use case.

## Java

Requirements:

- Java 21+
- Maven 3.9+

Run:

```bash
cd java
mvn spring-boot:run
```

Test:

```bash
cd java
mvn test
```

Health endpoint:

```text
GET http://localhost:8080/health
```

## Python

Requirements:

- Python 3.14
- `uv`

Install dependencies:

```bash
cd python
uv sync
```

Run:

```bash
cd python
uv run workshop-api
```

Test:

```bash
cd python
uv run pytest
```

Health endpoint:

```text
GET http://localhost:9090/health
```

## HTTP Requests

The repo includes a shared HTTP client request file in [`requests/health.http`](./modern-software-architecture-design-patterns-mono/requests/health.http) and environment definitions in [`requests/http-client.env.json`](./modern-software-architecture-design-patterns-mono/requests/http-client.env.json).

Select the environment before running the request:

- `java` -> `http://localhost:8080`
- `python` -> `http://localhost:9090`

Useful request files:

- [`requests/customer.http`](./modern-software-architecture-design-patterns-mono/requests/customer.http)
- [`requests/plan.http`](./modern-software-architecture-design-patterns-mono/requests/plan.http)
- [`requests/membership.http`](./modern-software-architecture-design-patterns-mono/requests/membership.http)
- [`requests/external-invoice-provider.http`](./modern-software-architecture-design-patterns-mono/requests/external-invoice-provider.http)

## Main Business Story

The main workshop reference flow is the membership lifecycle:

`activate -> invoice open -> overdue suspension -> payment received -> reactivation`

This story is intentionally implemented first in `exercise00_mixed` so later exercises can implement/refactor the same behavior into layered, hexagonal, vertical-slice, and richer domain-model variants.

Main steps:

1. Activate a membership with `POST /api/e00/memberships/activate`.
2. The system creates a membership immediately as `ACTIVE`.
3. An external invoice is created in the external invoice provider with status `OPEN`.
4. A local billing reference is stored so the membership service can reason about overdue and paid invoices later.
5. If the invoice stays open past its due date, `POST /api/e00/memberships/suspend-overdue` suspends the membership for `NON_PAYMENT`.
6. When payment is received, `POST /api/e00/memberships/payment-received` marks the billing reference as paid and may reactivate the membership if the period is still valid.

How to replay it:

1. Start either the Java app on `http://localhost:8080` or the Python app on `http://localhost:9090`.
2. Select the matching `java` or `python` environment in [`requests/http-client.env.json`](./modern-software-architecture-design-patterns-mono/requests/http-client.env.json).
3. Use [`requests/membership.http`](./modern-software-architecture-design-patterns-mono/requests/membership.http) for:
   - listing memberships
   - activating a membership
   - suspending overdue memberships
   - recording payment callbacks
4. Use [`requests/external-invoice-provider.http`](./modern-software-architecture-design-patterns-mono/requests/external-invoice-provider.http) to inspect invoices or simulate payment with `mark-paid`.

The Java application also seeds example customers, plans, memberships, and billing references in [`java/src/main/resources/data.sql`](./modern-software-architecture-design-patterns-mono/java/src/main/resources/data.sql) so the overdue and reactivation scenarios can be demonstrated immediately.


## CI

GitHub Actions runs both stacks on pushes to `main` and on pull requests via [`.github/workflows/ci.yml`](./modern-software-architecture-design-patterns-mono/.github/workflows/ci.yml).

- Java job: `mvn verify`
- Python job: `uv sync --all-groups`, `uv run ruff check`, `uv run pytest`

## Notes

- The local machine used for scaffolding this repo has Maven installed.
- `uv` was not installed locally, so the Python project was prepared for `uv` but not executed here.
- The local machine currently has Python 3.11 installed; the Python project is intentionally pinned to Python 3.14 for the workshop target.
