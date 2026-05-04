# modern-software-architecture-design-patterns-mono

Monorepo for a workshop that keeps the same application shape in two stacks:

- `java/`: Java 21, Spring Boot, Maven
- `python/`: Python 3.14, FastAPI, `uv` with `pyproject.toml`

## License

This workshop repository is provided under the [Codeartify Workshop License Agreement](./LICENSE.md).

## Structure

```text
.
├── java
│   ├── pom.xml
│   └── src
├── requests
│   ├── customer.http
│   ├── external-invoice-provider.http
│   ├── membership.http
│   └── plan.http
└── python
    ├── pyproject.toml
    ├── src
    └── tests
```

## Workshop Exercise Structure

Each workshop exercise lives on its own Git branch.

Branches:

- `main`
- `exercise1`
- `exercise1_solution`
- `exercise2_solution`
- `exercise3_solution`
- `exercise3b_solution`
- `exercise4_solution`
- `exercise5_solution`

Switch branches with:

```bash
git switch exercise1
git switch exercise1_solution
```

The HTTP API shape stays intentionally stable across branches so the same
request files can be used while comparing the implementations.

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

## HTTP Requests

The repo includes shared HTTP client request files in [`requests/`](./requests/)
and environment definitions in [`requests/http-client.env.json`](./requests/http-client.env.json).

Select the environment before running the request:

- `java` -> `http://localhost:8080`
- `python` -> `http://localhost:9090`

Useful request files:

- [`requests/customer.http`](./requests/customer.http)
- [`requests/plan.http`](./requests/plan.http)
- [`requests/membership.http`](./requests/membership.http)
- [`requests/external-invoice-provider.http`](./requests/external-invoice-provider.http)

## Main Business Story

Main steps:

1. Activate a membership with `POST /api/memberships/activate`.
2. The system creates a membership immediately as `ACTIVE`.
3. An external invoice is created in the external invoice provider with status `OPEN`.
4. A local billing reference is stored so the membership service can reason about overdue and paid invoices later.
5. An Email is sent out to the customer with the invoice details.

How to replay it:

1. Start either the Java app on `http://localhost:8080` or the Python app on `http://localhost:9090`.
2. Select the matching `java` or `python` environment in [
   `requests/http-client.env.json`](./requests/http-client.env.json).
3. Run `Create customer` in [`requests/customer.http`](./requests/customer.http). The response handler stores `customerId` for later requests.
4. Run `Create plan` in [`requests/plan.http`](./requests/plan.http). The response handler stores `planId` for later requests.
5. Run `Activate membership` in [`requests/membership.http`](./requests/membership.http). It uses the stored `customerId` and `planId`, then stores `membershipId`, `externalInvoiceId`, and `externalInvoiceReference`.
6. Continue with [`requests/membership.http`](./requests/membership.http) to list memberships, suspend overdue memberships, and record payment callbacks.
7. Use [`requests/external-invoice-provider.http`](./requests/external-invoice-provider.http) to inspect invoices or simulate payment with `mark-paid`.


## CI

GitHub Actions runs both stacks on pushes to `main` and on pull requests via [
`.github/workflows/ci.yml`](./.github/workflows/ci.yml).

- Java job: `mvn verify`
- Python job: `uv sync --all-groups`, `uv run ruff check`, `uv run pytest`
