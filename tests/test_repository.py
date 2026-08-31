"""Tests for the repository layer.

Each test runs inside a transaction that's rolled back afterward, so tests
never leave data behind or interfere with each other.
"""

import pytest
from sqlalchemy.orm import sessionmaker

from tickettracker.db import engine
from tickettracker.models import Agent, Base, Customer
from tickettracker.repository import (
    close_ticket,
    count_tickets_by_agent,
    create_ticket,
    get_open_tickets_for_customer,
)


@pytest.fixture(autouse=True, scope="session")
def setup_schema():
    """Create tables once for the test session (assumes ticketdb exists)."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session():
    """A session wrapped in a transaction that's always rolled back."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionForTest = sessionmaker(bind=connection)
    session = SessionForTest()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_customer(session):
    customer = Customer(name="Test Customer", email="test@example.com")
    session.add(customer)
    session.flush()
    return customer


@pytest.fixture
def sample_agent(session):
    agent = Agent(name="Test Agent", team="Tier 1")
    session.add(agent)
    session.flush()
    return agent


def test_create_ticket(session, sample_customer):
    ticket = create_ticket(session, sample_customer.id, "Broken login", priority="high")
    assert ticket.id is not None
    assert ticket.status == "open"
    assert ticket.priority == "high"


def test_get_open_tickets_for_customer_excludes_closed(session, sample_customer):
    open_ticket = create_ticket(session, sample_customer.id, "Issue A")
    closed_ticket = create_ticket(session, sample_customer.id, "Issue B")
    closed_ticket.status = "closed"
    session.flush()

    results = get_open_tickets_for_customer(session, sample_customer.id)

    assert open_ticket in results
    assert closed_ticket not in results


def test_close_ticket_changes_status(session, sample_customer):
    ticket = create_ticket(session, sample_customer.id, "Issue A")
    session.flush()

    closed = close_ticket(session, ticket.id)

    assert closed.status == "closed"


def test_close_ticket_returns_none_for_missing_id(session):
    result = close_ticket(session, 999999)
    assert result is None


def test_count_tickets_by_agent(session, sample_customer, sample_agent):
    t1 = create_ticket(session, sample_customer.id, "Issue A")
    t2 = create_ticket(session, sample_customer.id, "Issue B")
    t1.agent_id = sample_agent.id
    t2.agent_id = sample_agent.id
    session.flush()

    counts = count_tickets_by_agent(session)

    assert counts[sample_agent.name] == 2
