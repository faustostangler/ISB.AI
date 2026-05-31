from abc import ABC, abstractmethod

from isb.knowledge_organization.domain.document import Document


class DocumentRepositoryPort(ABC):
    """Port interface for storing and retrieving Document domain entities."""

    @abstractmethod
    def save(self, document: Document) -> None:
        """Saves or updates a document in the primary storage.

        Args:
            document: The Document entity to save.
        """
        pass


class TriageRepositoryPort(ABC):
    """Port interface for pushing documents into a manual review/triage queue."""

    @abstractmethod
    def push(self, document: Document) -> None:
        """Pushes a document to the triage review queue.

        Args:
            document: The Document entity requiring review.
        """
        pass
