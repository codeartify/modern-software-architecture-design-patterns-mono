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
└── python
    ├── pyproject.toml
    ├── src
    └── tests
```

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

The repo includes a shared HTTP client request file in [`requests/health.http`](/Users/ozihler/workspace2026/modern-software-architecture-design-patterns-mono/requests/health.http) and environment definitions in [`requests/http-client.env.json`](/Users/ozihler/workspace2026/modern-software-architecture-design-patterns-mono/requests/http-client.env.json).

Select the environment before running the request:

- `java` -> `http://localhost:8080`
- `python` -> `http://localhost:9090`

## Notes

- The local machine used for scaffolding this repo has Maven installed.
- `uv` was not installed locally, so the Python project was prepared for `uv` but not executed here.
- The local machine currently has Python 3.11 installed; the Python project is intentionally pinned to Python 3.14 for the workshop target.
