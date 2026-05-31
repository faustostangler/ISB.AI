import uuid
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from isb.shared_kernel.ports.task_queue import (
    TaskNotFoundError,
    TaskQueuePort,
    TaskSerializationError,
)


class ImmediateTaskQueueAdapter(TaskQueuePort):
    """Adapter executing tasks synchronously and immediately on the calling thread.

    Useful for hermetic unit testing and local development context.
    """

    def __init__(self) -> None:
        """Initializes the synchronous task queue with an empty handler registry."""
        self._handlers: dict[str, Callable[[Any], None]] = {}

    def register_handler(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = handler

    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id
