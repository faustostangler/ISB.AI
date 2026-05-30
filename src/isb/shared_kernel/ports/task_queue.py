from abc import ABC, abstractmethod

from pydantic import BaseModel


class TaskQueueError(Exception):
    """Base exception class for all task queue related errors."""
    pass


class TaskSerializationError(TaskQueueError):
    """Exception raised when a task payload fails serialization validation."""
    pass


class TaskNotFoundError(TaskQueueError):
    """Exception raised when a requested task handler or actor is not registered."""
    pass


class TaskQueuePort(ABC):
    """Abstract port defining the interface for scheduling background tasks.

    This port allows the domain/application layer to schedule tasks asynchronously
    without being coupled to the underlying message broker or execution engine.
    """

    @abstractmethod
    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues a task to run asynchronously.

        Args:
            task_name: The unique string identifier of the task (e.g., actor name).
            payload: A Pydantic BaseModel containing the serializable parameters.

        Returns:
            str: A unique task execution identifier (message ID).

        Raises:
            ValueError: If task_name is empty or invalid.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        # Step-by-step implementation walkthrough in adapters:
        # 1. Validate that the task_name is not empty or whitespace.
        # 2. Assert that the payload is serializable via model_dump_json().
        # 3. Retrieve the execution entity (handler/actor) by task_name.
        # 4. Dispatch the payload and return a unique identifier.
        raise NotImplementedError("Subclasses must implement the enqueue method")
