# Ticket Tracker (Python)

A support-ticket system backend built with Python, SQLAlchemy, and PostgreSQL — practicing real-world schema design, database migrations, and transactional testing.

## What this is

Three related tables — `customers`, `agents`, `tickets` — with realistic query patterns: filtering by status, joining tickets to agents, counting open tickets per agent. Built as a hands-on exercise in SQL fundamentals (joins, indexes, transactions) applied through a proper ORM layer, not just raw queries.

**Related repos:**
- [ticket-tracker-api](https://github.com/tjonadibernice/ticket-tracker-api) — a separate Node/Express REST API that serves the actual live application, reading/writing to the same database schema created here
- [ticket-tracker-ui](https://github.com/tjonadibernice/ticket-tracker-ui) — the React frontend, which talks to `ticket-tracker-api`

This repo's `repository.py` demonstrates the same domain implemented in Python/SQLAlchemy as a standalone, tested data access layer — it is not currently wired into the live frontend, but shares the same underlying database schema (managed here via Alembic migrations).

## Tech stack

- Python 3.11+, SQLAlchemy 2.0 (ORM)
- Alembic (database migrations)
- PostgreSQL
- pytest (transactional test isolation — each test runs in a rolled-back transaction)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires a running PostgreSQL instance. Create the database and apply migrations:
```bash
createdb ticketdb
alembic upgrade head
```

## Running tests

```bash
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ticketdb" pytest -v
```

## Schema

- `customers` — id, name, email (unique)
- `agents` — id, name, team
- `tickets` — id, customer_id (FK), agent_id (FK, nullable), subject, status, priority, created_at (indexed on `customer_id`)

## What I learned building this

- Alembic migrations as version control for schema changes, comparable to Flyway/Liquibase
- The difference between an ORM-level default (`default=`) and a real database-level default (`server_default=`) — only the latter applies when a different client (e.g. a separate Node service) writes to the same table
- Transactional test isolation: wrapping each test in its own transaction that's always rolled back, so tests never leave data behind or interfere with each other
