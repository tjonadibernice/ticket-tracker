"""Query functions for tickets — kept separate from any CLI/API layer so
it's directly testable, same pattern as secret-hunter's detector.py."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tickettracker.models import Agent, Ticket


def create_ticket(
    session: Session, customer_id: int, subject: str, priority: str = "medium"
) -> Ticket:
    ticket = Ticket(customer_id=customer_id, subject=subject, priority=priority)
    session.add(ticket)
    session.flush()  # assigns ticket.id without committing yet
    return ticket


def get_open_tickets_for_customer(session: Session, customer_id: int) -> list[Ticket]:
    stmt = select(Ticket).where(
        Ticket.customer_id == customer_id, Ticket.status == "open"
    )
    return list(session.scalars(stmt))


def count_tickets_by_agent(session: Session) -> dict[str, int]:
    """The same JOIN + GROUP BY query you ran directly in psql, expressed via SQLAlchemy."""
    stmt = (
        select(Agent.name, func.count(Ticket.id))
        .join(Ticket, Ticket.agent_id == Agent.id)
        .where(Ticket.status == "open")
        .group_by(Agent.name)
        .order_by(func.count(Ticket.id).desc())
    )
    return dict(session.execute(stmt).all())


def close_ticket(session: Session, ticket_id: int) -> Ticket | None:
    ticket = session.get(Ticket, ticket_id)
    if ticket is None:
        return None
    ticket.status = "closed"
    return ticket
