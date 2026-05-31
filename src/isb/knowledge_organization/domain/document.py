
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Domain model representing a document to be classified within the system."""

    document_id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Raw text content of the document")
    category: str | None = Field(default=None, description="The assigned category of the document")
    status: str = Field(default="Pending", description="The current status of the document classification")
    metadata: dict[str, str] = Field(default_factory=dict, description="Metadata tags associated with the document")
