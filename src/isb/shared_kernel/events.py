from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base class for all system domain events, enabling event-driven integration."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique event identifier")
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp indicating when the event occurred (UTC)",
    )
